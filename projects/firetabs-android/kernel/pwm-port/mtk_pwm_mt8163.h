/* SPDX-License-Identifier: GPL-2.0-only */
/* Conservative legacy-written fields; not a claim about hardware maxima. */
#define MT8163_PWM_PERIOD_MASK 0x3ffU
#define MT8163_PWM_UNQUALIFIED_PERIOD GENMASK(11, 10)

static bool mtk_pwm_mt8163(struct mtk_disp_pwm *mdp)
{
	return mdp->data && mdp->data->mt8163_strict;
}

static void mtk_pwm_strict_release(struct mtk_disp_pwm *mdp)
{
	if (mdp->strict_mm_owned) {
		clk_disable_unprepare(mdp->clk_mm);
		mdp->strict_mm_owned = false;
	}
	if (mdp->strict_main_owned) {
		clk_disable_unprepare(mdp->clk_main);
		mdp->strict_main_owned = false;
	}
}

static int mtk_pwm_strict_acquire(struct mtk_disp_pwm *mdp)
{
	int ret;

	if (mdp->strict_main_owned != mdp->strict_mm_owned) {
		mdp->strict_fault = true;
		return -EIO;
	}
	if (mdp->strict_main_owned)
		return 0;
	ret = clk_prepare_enable(mdp->clk_main);
	if (ret)
		return ret;
	mdp->strict_main_owned = true;
	ret = clk_prepare_enable(mdp->clk_mm);
	if (ret) {
		mtk_pwm_strict_release(mdp);
		return ret;
	}
	mdp->strict_mm_owned = true;
	return 0;
}

static void mtk_pwm_strict_commit(struct mtk_disp_pwm *mdp)
{
	/* The selected active legacy sequence writes the whole commit word. */
	writel(1, mdp->base + mdp->data->commit);
	writel(0, mdp->base + mdp->data->commit);
}

static void mtk_pwm_strict_off(struct mtk_disp_pwm *mdp)
{
	mtk_disp_pwm_update_bits(mdp, DISP_PWM_EN, BIT(0), 0);
	mtk_pwm_strict_commit(mdp);
	mdp->enabled = false;
	mtk_pwm_strict_release(mdp);
}

static void mtk_pwm_strict_cleanup(void *data)
{
	struct mtk_disp_pwm *mdp = data;

	mutex_lock(&mdp->strict_lock);
	if (mdp->strict_stopping)
		goto out;
	mdp->strict_stopping = true;
	mdp->strict_ready = false;
	if (mdp->strict_main_owned != mdp->strict_mm_owned) {
		mdp->strict_fault = true;
		dev_err(mdp->strict_dev, "MT8163 PWM cleanup ownership unresolved\n");
		mtk_pwm_strict_release(mdp);
	} else if (mdp->strict_main_owned) {
		mtk_pwm_strict_off(mdp);
	}
	/* Never acquire power to stop hardware this instance did not own. */
out:
	mutex_unlock(&mdp->strict_lock);
}

static int mtk_disp_pwm_apply(struct pwm_chip *chip, struct pwm_device *pwm,
			      const struct pwm_state *state)
{
	struct mtk_disp_pwm *mdp = to_mtk_disp_pwm(chip);
	u64 rate, product, duty_product, cycles, divider, denominator, ticks, high;
	bool had_power;
	int ret;

	if (!mtk_pwm_mt8163(mdp))
		return mtk_disp_pwm_apply_legacy(chip, pwm, state);
	mutex_lock(&mdp->strict_lock);
	if (!mdp->strict_ready || mdp->strict_stopping) {
		ret = -ENODEV;
		goto out;
	}
	/* PWM core expressly ignores all other fields of a disabled state. */
	if (!state->enabled) {
		ret = mtk_pwm_strict_acquire(mdp);
		if (!ret)
			mtk_pwm_strict_off(mdp);
		goto out;
	}
	if (mdp->strict_fault) {
		ret = -EIO;
		goto out;
	}
	if (!state->period || state->duty_cycle > state->period ||
	    state->polarity != PWM_POLARITY_NORMAL) {
		ret = -EINVAL;
		goto out;
	}
	had_power = mdp->strict_main_owned && mdp->strict_mm_owned;
	ret = mtk_pwm_strict_acquire(mdp);
	if (ret)
		goto out;
	rate = clk_get_rate(mdp->clk_main);
	if (!rate) {
		ret = -ERANGE;
		goto release;
	}
	if (check_mul_overflow(state->period, rate, &product) ||
	    check_mul_overflow(state->duty_cycle, rate, &duty_product)) {
		ret = -EOVERFLOW;
		goto release;
	}
	cycles = div64_u64(product, NSEC_PER_SEC);
	if (!cycles) {
		ret = -ERANGE;
		goto release;
	}
	divider = div64_u64(cycles - 1, MT8163_PWM_PERIOD_MASK + 1);
	if (divider > PWM_CLKDIV_MAX) {
		ret = -ERANGE;
		goto release;
	}
	denominator = NSEC_PER_SEC * (divider + 1);
	ticks = div64_u64(product, denominator);
	high = div64_u64(duty_product, denominator);
	if (!ticks || ticks > MT8163_PWM_PERIOD_MASK + 1 ||
	    high > ticks || high > 0x1fff) {
		ret = -ERANGE;
		goto release;
	}
	/* Do not reinterpret a pre-existing wider-period configuration. */
	if (readl(mdp->base + mdp->data->con1) & MT8163_PWM_UNQUALIFIED_PERIOD) {
		ret = -EOPNOTSUPP;
		goto release;
	}
	mtk_disp_pwm_update_bits(mdp, mdp->data->con0, PWM_CLKDIV_MASK,
				 (u32)divider << PWM_CLKDIV_SHIFT);
	mtk_disp_pwm_update_bits(mdp, mdp->data->con1,
				 MT8163_PWM_PERIOD_MASK | PWM_HIGH_WIDTH_MASK,
				 (u32)(ticks - 1) | ((u32)high << PWM_HIGH_WIDTH_SHIFT));
	mtk_disp_pwm_update_bits(mdp, DISP_PWM_EN, BIT(0), BIT(0));
	mtk_pwm_strict_commit(mdp);
	mdp->enabled = true;
	ret = 0;
	goto out;
release:
	/* Invalid updates retain a previous successful request and its references. */
	if (!had_power)
		mtk_pwm_strict_release(mdp);
out:
	mutex_unlock(&mdp->strict_lock);
	return ret;
}

static u64 mtk_pwm_strict_ceil(u64 numerator, u64 denominator)
{
	u64 quotient = div64_u64(numerator, denominator);

	return quotient + (numerator - quotient * denominator != 0);
}

static int mtk_disp_pwm_get_state(struct pwm_chip *chip, struct pwm_device *pwm,
				  struct pwm_state *state)
{
	struct mtk_disp_pwm *mdp = to_mtk_disp_pwm(chip);
	struct pwm_state result = { 0 };
	u64 rate, ticks, high, scale;
	u32 con0, con1, enable;
	bool had_power;
	int ret;

	if (!mtk_pwm_mt8163(mdp))
		return mtk_disp_pwm_get_state_legacy(chip, pwm, state);
	mutex_lock(&mdp->strict_lock);
	if (!mdp->strict_ready || mdp->strict_stopping || mdp->strict_fault) {
		ret = -EIO;
		goto out;
	}
	had_power = mdp->strict_main_owned && mdp->strict_mm_owned;
	ret = mtk_pwm_strict_acquire(mdp);
	if (ret)
		goto out;
	rate = clk_get_rate(mdp->clk_main);
	if (!rate) {
		ret = -ERANGE;
		goto release;
	}
	con0 = readl(mdp->base + mdp->data->con0);
	con1 = readl(mdp->base + mdp->data->con1);
	enable = readl(mdp->base + DISP_PWM_EN);
	if (con1 & MT8163_PWM_UNQUALIFIED_PERIOD) {
		ret = -EOPNOTSUPP;
		goto release;
	}
	ticks = (con1 & MT8163_PWM_PERIOD_MASK) + 1;
	high = FIELD_GET(PWM_HIGH_WIDTH_MASK, con1);
	if (high > ticks) {
		ret = -EOPNOTSUPP;
		goto release;
	}
	scale = (u64)(FIELD_GET(PWM_CLKDIV_MASK, con0) + 1) * NSEC_PER_SEC;
	result.period = mtk_pwm_strict_ceil(ticks * scale, rate);
	result.duty_cycle = mtk_pwm_strict_ceil(high * scale, rate);
	result.enabled = !!(enable & BIT(0));
	result.polarity = PWM_POLARITY_NORMAL;
	*state = result;
	ret = 0;
release:
	if (!had_power)
		mtk_pwm_strict_release(mdp);
out:
	mutex_unlock(&mdp->strict_lock);
	return ret;
}

static int mtk_pwm_strict_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct resource *res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
	struct pwm_chip *chip;
	struct mtk_disp_pwm *mdp;
	int ret;

	if (!res || res->end < res->start || (res->start & 3) ||
	    resource_size(res) < 0x18 || (resource_size(res) & 3) ||
	    !dev->of_node || !of_find_property(dev->of_node, "power-domains", NULL) ||
	    of_find_property(dev->of_node, "assigned-clocks", NULL) ||
	    of_find_property(dev->of_node, "assigned-clock-parents", NULL) ||
	    of_find_property(dev->of_node, "assigned-clock-rates", NULL))
		return -EINVAL;
	chip = devm_pwmchip_alloc(dev, 1, sizeof(*mdp));
	if (IS_ERR(chip))
		return PTR_ERR(chip);
	mdp = to_mtk_disp_pwm(chip);
	mdp->data = of_device_get_match_data(dev);
	mdp->strict_dev = dev;
	mutex_init(&mdp->strict_lock);
	mdp->base = devm_platform_ioremap_resource(pdev, 0);
	if (IS_ERR(mdp->base))
		return PTR_ERR(mdp->base);
	mdp->clk_main = devm_clk_get(dev, "main");
	if (IS_ERR(mdp->clk_main))
		return PTR_ERR(mdp->clk_main);
	mdp->clk_mm = devm_clk_get(dev, "mm");
	if (IS_ERR(mdp->clk_mm))
		return PTR_ERR(mdp->clk_mm);
	ret = devm_add_action_or_reset(dev, mtk_pwm_strict_cleanup, mdp);
	if (ret)
		return ret;
	chip->ops = &mtk_disp_pwm_ops;
	mdp->strict_ready = true;
	ret = devm_pwmchip_add(dev, chip);
	if (ret)
		mtk_pwm_strict_cleanup(mdp);
	return ret;
}

static int mtk_disp_pwm_probe(struct platform_device *pdev)
{
	const struct mtk_pwm_data *data = of_device_get_match_data(&pdev->dev);

	if (data && data->mt8163_strict)
		return mtk_pwm_strict_probe(pdev);
	return mtk_disp_pwm_probe_legacy(pdev);
}
