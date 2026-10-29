/* SPDX-License-Identifier: GPL-2.0-only */
/* Included after the legacy helpers; MT8163 source-only backend, not a panel. */
static bool mtk_dsi_mt8163(struct mtk_dsi *dsi)
{
	return dsi->driver_data && dsi->driver_data->mt8163_strict;
}

static void mtk_dsi_strict_fault(struct mtk_dsi *dsi, int error)
{
	dsi->strict_fault = true;
	if (dsi->strict_irq_enabled) {
		disable_irq(dsi->strict_irq);
		dsi->strict_irq_enabled = false;
	}
	dev_err(dsi->host.dev, "MT8163 DSI state unqualified after error %d\n", error);
}

static int mtk_dsi_strict_release(struct mtk_dsi *dsi)
{
	int ret;

	if (dsi->strict_digital_owned) {
		clk_disable_unprepare(dsi->digital_clk);
		dsi->strict_digital_owned = false;
	}
	if (dsi->strict_engine_owned) {
		clk_disable_unprepare(dsi->engine_clk);
		dsi->strict_engine_owned = false;
	}
	if (dsi->strict_phy_owned) {
		ret = phy_power_off(dsi->phy);
		if (ret) {
			mtk_dsi_strict_fault(dsi, ret);
			return ret;
		}
		dsi->strict_phy_owned = false;
	}
	return 0;
}

static int mtk_dsi_strict_poweron(struct mtk_dsi *dsi)
{
	u64 product, rate;
	int bpp, ret;

	if (!dsi->strict_ready)
		return -EPROBE_DEFER;
	if (dsi->strict_fault)
		return -EIO;
	if (dsi->refcount) {
		if (!dsi->strict_active || dsi->refcount == INT_MAX)
			return -EOVERFLOW;
		dsi->refcount++;
		return 0;
	}
	if (dsi->lanes < 1 || dsi->lanes > 4)
		return -EINVAL;
	bpp = mipi_dsi_pixel_format_to_bpp(dsi->format);
	if (bpp <= 0)
		return bpp < 0 ? bpp : -EINVAL;
	if (check_mul_overflow((u64)dsi->vm.pixelclock, (u64)bpp, &product) ||
	    check_add_overflow(product, (u64)dsi->lanes - 1, &product))
		return -EOVERFLOW;
	rate = div_u64(product, dsi->lanes);
	if (rate < 50000000 || rate > 1250000000)
		return -ERANGE;
	ret = clk_set_rate(dsi->hs_clk, rate);
	if (ret)
		return ret;
	ret = phy_power_on(dsi->phy);
	if (ret)
		return ret;
	dsi->strict_phy_owned = true;
	ret = clk_prepare_enable(dsi->engine_clk);
	if (ret)
		goto fail;
	dsi->strict_engine_owned = true;
	ret = clk_prepare_enable(dsi->digital_clk);
	if (ret)
		goto fail;
	dsi->strict_digital_owned = true;
	dsi->data_rate = rate;
	mtk_dsi_set_cmd_mode(dsi);
	mtk_dsi_enable(dsi);
	mtk_dsi_reset_engine(dsi);
	mtk_dsi_phy_timconfig(dsi);
	mtk_dsi_ps_control(dsi, true);
	mtk_dsi_set_vm_cmd(dsi);
	mtk_dsi_config_vdo_timing(dsi);
	mtk_dsi_set_interrupt_enable(dsi);
	dsi->strict_active = true;
	dsi->refcount = 1;
	enable_irq(dsi->strict_irq);
	dsi->strict_irq_enabled = true;
	return 0;
fail:
	/* Keep the primary error; failed release retains its ownership and fault. */
	mtk_dsi_strict_release(dsi);
	return ret;
}

static int mtk_dsi_poweron(struct mtk_dsi *dsi)
{
	int ret;

	if (!mtk_dsi_mt8163(dsi))
		return mtk_dsi_poweron_legacy(dsi);
	mutex_lock(&dsi->strict_lock);
	ret = mtk_dsi_strict_poweron(dsi);
	mutex_unlock(&dsi->strict_lock);
	return ret;
}

static void mtk_dsi_strict_poweroff(struct mtk_dsi *dsi)
{
	if (!dsi->refcount)
		return;
	if (--dsi->refcount)
		return;
	dsi->strict_active = false;
	if (dsi->strict_irq_enabled) {
		disable_irq(dsi->strict_irq);
		dsi->strict_irq_enabled = false;
	}
	mtk_dsi_stop(dsi);
	mtk_dsi_set_cmd_mode(dsi);
	mtk_dsi_reset_engine(dsi);
	mtk_dsi_lane0_ulp_mode_enter(dsi);
	mtk_dsi_clk_ulp_mode_enter(dsi);
	writel(0, dsi->regs + DSI_TXRX_CTRL);
	mtk_dsi_disable(dsi);
	dsi->enabled = false;
	dsi->lanes_ready = false;
	mtk_dsi_strict_release(dsi);
}

static void mtk_dsi_poweroff(struct mtk_dsi *dsi)
{
	if (!mtk_dsi_mt8163(dsi)) {
		mtk_dsi_poweroff_legacy(dsi);
		return;
	}
	mutex_lock(&dsi->strict_lock);
	mtk_dsi_strict_poweroff(dsi);
	mutex_unlock(&dsi->strict_lock);
}

static void mtk_output_dsi_enable(struct mtk_dsi *dsi)
{
	if (!mtk_dsi_mt8163(dsi)) {
		mtk_output_dsi_enable_legacy(dsi);
		return;
	}
	mutex_lock(&dsi->strict_lock);
	if (dsi->strict_ready && dsi->strict_active && dsi->refcount &&
	    !dsi->strict_fault)
		mtk_output_dsi_enable_legacy(dsi);
	mutex_unlock(&dsi->strict_lock);
}

static void mtk_dsi_set_interrupt_enable(struct mtk_dsi *dsi)
{
	if (!mtk_dsi_mt8163(dsi)) {
		mtk_dsi_set_interrupt_enable_legacy(dsi);
		return;
	}
	writel(LPRX_RD_RDY_INT_FLAG | CMD_DONE_INT_FLAG, dsi->regs + DSI_INTEN);
	writel(BIT(1), dsi->regs + DSI_RACK);
}

static void mtk_dsi_irq_data_set(struct mtk_dsi *dsi, u32 bit)
{
	unsigned long flags;

	if (!mtk_dsi_mt8163(dsi)) {
		mtk_dsi_irq_data_set_legacy(dsi, bit);
		return;
	}
	spin_lock_irqsave(&dsi->strict_irq_lock, flags);
	dsi->irq_data |= bit;
	spin_unlock_irqrestore(&dsi->strict_irq_lock, flags);
}

static void mtk_dsi_irq_data_clear(struct mtk_dsi *dsi, u32 bit)
{
	unsigned long flags;

	if (!mtk_dsi_mt8163(dsi)) {
		mtk_dsi_irq_data_clear_legacy(dsi, bit);
		return;
	}
	spin_lock_irqsave(&dsi->strict_irq_lock, flags);
	dsi->irq_data &= ~bit;
	spin_unlock_irqrestore(&dsi->strict_irq_lock, flags);
}

static irqreturn_t mtk_dsi_irq(int irq, void *data)
{
	struct mtk_dsi *dsi = data;
	u32 status;

	if (!mtk_dsi_mt8163(dsi))
		return mtk_dsi_irq_legacy(irq, data);
	if (!READ_ONCE(dsi->strict_active) || READ_ONCE(dsi->strict_fault))
		return IRQ_NONE;
	status = readl(dsi->regs + DSI_INTSTA) &
		 (LPRX_RD_RDY_INT_FLAG | CMD_DONE_INT_FLAG);
	if (!status)
		return IRQ_NONE;
	mtk_dsi_mask(dsi, DSI_INTSTA, status, 0);
	mtk_dsi_irq_data_set(dsi, status);
	wake_up_interruptible(&dsi->irq_wait_queue);
	return IRQ_HANDLED;
}

static s32 mtk_dsi_switch_to_cmd_mode(struct mtk_dsi *dsi, u8 flag, u32 timeout)
{
	if (!mtk_dsi_mt8163(dsi))
		return mtk_dsi_switch_to_cmd_mode_legacy(dsi, flag, timeout);
	mtk_dsi_irq_data_clear(dsi, flag);
	mtk_dsi_set_cmd_mode(dsi);
	return 0;
}

static int mtk_dsi_bind(struct device *dev, struct device *master, void *data)
{
	struct mtk_dsi *dsi = dev_get_drvdata(dev);
	int ret;

	if (!mtk_dsi_mt8163(dsi))
		return mtk_dsi_bind_legacy(dev, master, data);
	mutex_lock(&dsi->strict_lock);
	if (!dsi->strict_ready || dsi->strict_binding || dsi->strict_encoder_owned ||
	    dsi->refcount || dsi->strict_fault) {
		ret = !dsi->strict_ready ? -EPROBE_DEFER : -EBUSY;
		goto unlock;
	}
	ret = device_reset(dev);
	if (ret)
		goto unlock;
	dsi->strict_binding = true;
	mutex_unlock(&dsi->strict_lock);
	ret = mtk_dsi_encoder_init(data, dsi);
	mutex_lock(&dsi->strict_lock);
	dsi->strict_binding = false;
	if (!ret)
		dsi->strict_encoder_owned = true;
unlock:
	mutex_unlock(&dsi->strict_lock);
	return ret;
}

static void mtk_dsi_unbind(struct device *dev, struct device *master, void *data)
{
	struct mtk_dsi *dsi = dev_get_drvdata(dev);

	if (!mtk_dsi_mt8163(dsi)) {
		mtk_dsi_unbind_legacy(dev, master, data);
		return;
	}
	mutex_lock(&dsi->strict_lock);
	if (dsi->refcount) {
		dsi->refcount = 1;
		mtk_dsi_strict_poweroff(dsi);
	}
	if (dsi->strict_encoder_owned && !dsi->strict_phy_owned) {
		drm_encoder_cleanup(&dsi->encoder);
		dsi->strict_encoder_owned = false;
	}
	mutex_unlock(&dsi->strict_lock);
}

static int mtk_dsi_host_attach(struct mipi_dsi_host *host,
			       struct mipi_dsi_device *device)
{
	struct mtk_dsi *dsi = host_to_dsi(host);
	struct drm_bridge *next, *old_bridge;
	unsigned int old_lanes;
	enum mipi_dsi_pixel_format old_format;
	unsigned long old_flags;
	int ret;

	if (!mtk_dsi_mt8163(dsi))
		return mtk_dsi_host_attach_legacy(host, device);
	mutex_lock(&dsi->strict_lock);
	if (!dsi->strict_ready || dsi->strict_pending || dsi->strict_attached ||
	    dsi->strict_fault) {
		ret = !dsi->strict_ready ? -EPROBE_DEFER : -EBUSY;
		goto unlock;
	}
	if (device->lanes < 1 || device->lanes > 4 ||
	    mipi_dsi_pixel_format_to_bpp(device->format) <= 0) {
		ret = -EINVAL;
		goto unlock;
	}
	next = devm_drm_of_get_bridge(host->dev, host->dev->of_node, 1, 0);
	if (IS_ERR(next)) {
		ret = PTR_ERR(next);
		if (ret == -EPROBE_DEFER)
			goto unlock;
		next = devm_drm_of_get_bridge(host->dev, host->dev->of_node, 0, 0);
		if (IS_ERR(next)) {
			ret = PTR_ERR(next);
			goto unlock;
		}
	}
	old_lanes = dsi->lanes;
	old_format = dsi->format;
	old_flags = dsi->mode_flags;
	old_bridge = dsi->next_bridge;
	dsi->lanes = device->lanes;
	dsi->format = device->format;
	dsi->mode_flags = device->mode_flags;
	dsi->next_bridge = next;
	dsi->strict_pending = true;
	dsi->strict_attached = true;
	drm_bridge_add(&dsi->bridge);
	dsi->strict_bridge_owned = true;
	mutex_unlock(&dsi->strict_lock);
	ret = component_add(host->dev, &mtk_dsi_component_ops);
	mutex_lock(&dsi->strict_lock);
	dsi->strict_pending = false;
	if (ret) {
		if (dsi->refcount) {
			dsi->refcount = 1;
			mtk_dsi_strict_poweroff(dsi);
		}
		if (dsi->strict_encoder_owned && !dsi->strict_phy_owned) {
			drm_encoder_cleanup(&dsi->encoder);
			dsi->strict_encoder_owned = false;
		}
		if (dsi->strict_phy_owned)
			goto unlock;
		drm_bridge_remove(&dsi->bridge);
		dsi->strict_bridge_owned = false;
		dsi->strict_attached = false;
		dsi->lanes = old_lanes;
		dsi->format = old_format;
		dsi->mode_flags = old_flags;
		dsi->next_bridge = old_bridge;
	} else {
		dsi->strict_component_owned = true;
	}
unlock:
	mutex_unlock(&dsi->strict_lock);
	return ret;
}

static int mtk_dsi_host_detach(struct mipi_dsi_host *host,
			       struct mipi_dsi_device *device)
{
	struct mtk_dsi *dsi = host_to_dsi(host);
	bool component, bridge;

	if (!mtk_dsi_mt8163(dsi))
		return mtk_dsi_host_detach_legacy(host, device);
	mutex_lock(&dsi->strict_lock);
	if (dsi->strict_pending || dsi->strict_binding) {
		mutex_unlock(&dsi->strict_lock);
		return -EBUSY;
	}
	if (dsi->refcount) {
		dsi->refcount = 1;
		mtk_dsi_strict_poweroff(dsi);
	}
	if (dsi->strict_phy_owned) {
		mutex_unlock(&dsi->strict_lock);
		return -EIO;
	}
	component = dsi->strict_component_owned;
	bridge = dsi->strict_bridge_owned;
	dsi->strict_pending = true;
	dsi->strict_attached = false;
	dsi->strict_component_owned = false;
	mutex_unlock(&dsi->strict_lock);
	if (component)
		component_del(host->dev, &mtk_dsi_component_ops);
	if (bridge)
		drm_bridge_remove(&dsi->bridge);
	mutex_lock(&dsi->strict_lock);
	dsi->strict_bridge_owned = false;
	dsi->strict_pending = false;
	dsi->lanes = 0;
	dsi->next_bridge = NULL;
	mutex_unlock(&dsi->strict_lock);
	return 0;
}

static int mtk_dsi_strict_message(const struct mipi_dsi_msg *msg)
{
	bool read;

	if (!msg || (msg->tx_len && !msg->tx_buf) || msg->tx_len > 248 ||
	    (msg->flags & ~(MIPI_DSI_MSG_REQ_ACK | MIPI_DSI_MSG_USE_LPM)))
		return -EINVAL;
	if (!mipi_dsi_packet_format_is_short(msg->type) &&
	    !mipi_dsi_packet_format_is_long(msg->type))
		return -EINVAL;
	if (mipi_dsi_packet_format_is_short(msg->type) && msg->tx_len > 2)
		return -EMSGSIZE;
	read = MTK_DSI_HOST_IS_READ(msg->type);
	if (read ? (!msg->rx_buf || !msg->rx_len || msg->rx_len > 10) : msg->rx_len)
		return -EINVAL;
	return 0;
}

static void mtk_dsi_cmdq(struct mtk_dsi *dsi, const struct mipi_dsi_msg *msg)
{
	const u8 *buf;
	u32 config, size, offset, mask, val, i;

	if (!mtk_dsi_mt8163(dsi)) {
		mtk_dsi_cmdq_legacy(dsi, msg);
		return;
	}
	if (mtk_dsi_strict_message(msg))
		return;
	buf = msg->tx_buf;
	config = MTK_DSI_HOST_IS_READ(msg->type) ? BTA :
		 (msg->tx_len > 2 ? LONG_PACKET : SHORT_PACKET);
	if (!(msg->flags & MIPI_DSI_MSG_USE_LPM))
		config |= BIT(3);
	if (msg->tx_len > 2) {
		size = 1 + (msg->tx_len + 3) / 4;
		offset = 4;
		mask = CONFIG | DATA_ID | DATA_0 | DATA_1;
		val = (msg->tx_len << 16) | (msg->type << 8) | config;
	} else {
		size = 1;
		offset = 2;
		mask = CONFIG | DATA_ID;
		val = (msg->type << 8) | config;
	}
	for (i = 0; i < msg->tx_len; i++)
		mtk_dsi_mask(dsi, (dsi->driver_data->reg_cmdq_off + offset + i) & ~3U,
			     0xffU << (((i + offset) & 3) * 8),
			     (u32)buf[i] << (((i + offset) & 3) * 8));
	mtk_dsi_mask(dsi, dsi->driver_data->reg_cmdq_off, mask, val);
	mtk_dsi_mask(dsi, DSI_CMDQ_SIZE, CMDQ_SIZE, size);
}

static ssize_t mtk_dsi_host_transfer(struct mipi_dsi_host *host,
				 const struct mipi_dsi_msg *msg)
{
	struct mtk_dsi *dsi = host_to_dsi(host);
	u32 mode, val;
	u8 flag = CMD_DONE_INT_FLAG, bytes[16];
	int ret, count = 0, i, start;
	long waited;

	if (!mtk_dsi_mt8163(dsi))
		return mtk_dsi_host_transfer_legacy(host, msg);
	ret = mtk_dsi_strict_message(msg);
	if (ret)
		return ret;
	mutex_lock(&dsi->strict_lock);
	if (dsi->strict_fault || !dsi->strict_active || !dsi->refcount ||
	    !dsi->strict_attached) {
		ret = -EPIPE;
		goto out;
	}
	mode = readl(dsi->regs + DSI_MODE_CTRL);
	if (mode & MODE) {
		mtk_dsi_stop(dsi);
		mtk_dsi_set_cmd_mode(dsi);
	}
	ret = readl_poll_timeout(dsi->regs + DSI_INTSTA, val, !(val & DSI_BUSY),
				 4, 2000000);
	if (ret)
		goto fault;
	if (MTK_DSI_HOST_IS_READ(msg->type))
		flag |= LPRX_RD_RDY_INT_FLAG;
	mtk_dsi_irq_data_clear(dsi, flag);
	mtk_dsi_lane_ready(dsi);
	mtk_dsi_cmdq(dsi, msg);
	mtk_dsi_start(dsi);
	waited = wait_event_interruptible_timeout(dsi->irq_wait_queue,
		(READ_ONCE(dsi->irq_data) & flag) == flag, msecs_to_jiffies(2000));
	if (waited <= 0) {
		ret = waited < 0 ? waited : -ETIMEDOUT;
		goto fault;
	}
	ret = msg->tx_len;
	if (MTK_DSI_HOST_IS_READ(msg->type)) {
		for (i = 0; i < 16; i++)
			bytes[i] = readb(dsi->regs + DSI_RX_DATA0 + i);
		switch (bytes[0]) {
		case MIPI_DSI_RX_GENERIC_SHORT_READ_RESPONSE_1BYTE:
		case MIPI_DSI_RX_DCS_SHORT_READ_RESPONSE_1BYTE:
			count = 1; start = 1; break;
		case MIPI_DSI_RX_GENERIC_SHORT_READ_RESPONSE_2BYTE:
		case MIPI_DSI_RX_DCS_SHORT_READ_RESPONSE_2BYTE:
			count = 2; start = 1; break;
		case MIPI_DSI_RX_GENERIC_LONG_READ_RESPONSE:
		case MIPI_DSI_RX_DCS_LONG_READ_RESPONSE:
			count = bytes[1] | ((u32)bytes[2] << 8); start = 4; break;
		default:
			ret = -EPROTO;
			goto fault;
		}
		count = min_t(size_t, count, msg->rx_len);
		memcpy(msg->rx_buf, bytes + start, count);
		ret = count;
	}
	if (mode & MODE) {
		mtk_dsi_set_mode(dsi);
		mtk_dsi_start(dsi);
	}
	goto out;
fault:
	mtk_dsi_strict_fault(dsi, ret);
out:
	mutex_unlock(&dsi->strict_lock);
	return ret;
}

static int mtk_dsi_strict_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct resource *res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
	struct mtk_dsi *dsi;
	int irq, ret;

	if (!res || res->end < res->start || (res->start & 3) ||
	    resource_size(res) < 0x400 || (resource_size(res) & 3) ||
	    !dev->of_node || !of_find_property(dev->of_node, "resets", NULL) ||
	    !of_find_property(dev->of_node, "power-domains", NULL))
		return -EINVAL;
	dsi = devm_drm_bridge_alloc(dev, struct mtk_dsi, bridge, &mtk_dsi_bridge_funcs);
	if (IS_ERR(dsi))
		return PTR_ERR(dsi);
	dsi->driver_data = of_device_get_match_data(dev);
	mutex_init(&dsi->strict_lock);
	spin_lock_init(&dsi->strict_irq_lock);
	dsi->engine_clk = devm_clk_get(dev, "engine");
	if (IS_ERR(dsi->engine_clk))
		return PTR_ERR(dsi->engine_clk);
	dsi->digital_clk = devm_clk_get(dev, "digital");
	if (IS_ERR(dsi->digital_clk))
		return PTR_ERR(dsi->digital_clk);
	dsi->hs_clk = devm_clk_get(dev, "hs");
	if (IS_ERR(dsi->hs_clk))
		return PTR_ERR(dsi->hs_clk);
	dsi->regs = devm_platform_ioremap_resource(pdev, 0);
	if (IS_ERR(dsi->regs))
		return PTR_ERR(dsi->regs);
	dsi->phy = devm_phy_get(dev, "dphy");
	if (IS_ERR(dsi->phy))
		return PTR_ERR(dsi->phy);
	irq = platform_get_irq(pdev, 0);
	if (irq < 0)
		return irq;
	dsi->strict_irq = irq;
	dsi->host.ops = &mtk_dsi_ops;
	dsi->host.dev = dev;
	init_waitqueue_head(&dsi->irq_wait_queue);
	platform_set_drvdata(pdev, dsi);
	ret = mipi_dsi_host_register(&dsi->host);
	if (ret)
		return ret;
	dsi->strict_host_registered = true;
	ret = devm_request_irq(dev, irq, mtk_dsi_irq, IRQF_NO_AUTOEN, dev_name(dev), dsi);
	if (ret) {
		mipi_dsi_host_unregister(&dsi->host);
		dsi->strict_host_registered = false;
		return ret;
	}
	dsi->bridge.of_node = dev->of_node;
	dsi->bridge.type = DRM_MODE_CONNECTOR_DSI;
	dsi->strict_ready = true;
	return 0;
}

static int mtk_dsi_probe(struct platform_device *pdev)
{
	const struct mtk_dsi_driver_data *data = of_device_get_match_data(&pdev->dev);

	if (data && data->mt8163_strict)
		return mtk_dsi_strict_probe(pdev);
	return mtk_dsi_probe_legacy(pdev);
}

static void mtk_dsi_remove(struct platform_device *pdev)
{
	struct mtk_dsi *dsi = platform_get_drvdata(pdev);
	int ret;

	if (!mtk_dsi_mt8163(dsi)) {
		mtk_dsi_remove_legacy(pdev);
		return;
	}
	ret = mtk_dsi_host_detach(&dsi->host, NULL);
	if (ret)
		dev_err(&pdev->dev, "MT8163 detach cleanup unresolved: %d\n", ret);
	mutex_lock(&dsi->strict_lock);
	dsi->strict_ready = false;
	mutex_unlock(&dsi->strict_lock);
	if (dsi->strict_host_registered) {
		mipi_dsi_host_unregister(&dsi->host);
		dsi->strict_host_registered = false;
	}
}

static enum drm_mode_status
mtk_dsi_bridge_mode_valid(struct drm_bridge *bridge,
                          const struct drm_display_info *info,
                          const struct drm_display_mode *mode)
{
 struct mtk_dsi *dsi = bridge_to_dsi(bridge);
 u64 rate;
 int bpp;

 if (!mtk_dsi_mt8163(dsi))
  return mtk_dsi_bridge_mode_valid_legacy(bridge, info, mode);
 if (mode->clock <= 0 || dsi->lanes < 1 || dsi->lanes > 4)
  return MODE_ERROR;
 bpp = mipi_dsi_pixel_format_to_bpp(dsi->format);
 if (bpp <= 0 || check_mul_overflow((u64)mode->clock, (u64)bpp * 1000, &rate) ||
     check_add_overflow(rate, (u64)dsi->lanes - 1, &rate))
  return MODE_ERROR;
 rate = div_u64(rate, dsi->lanes);
 if (rate < 50000000)
  return MODE_CLOCK_LOW;
 if (rate > 1250000000)
  return MODE_CLOCK_HIGH;
 return MODE_OK;
}

static void mtk_dsi_bridge_mode_set(struct drm_bridge *bridge,
                                  const struct drm_display_mode *mode,
                                  const struct drm_display_mode *adjusted)
{
 struct mtk_dsi *dsi = bridge_to_dsi(bridge);

 if (!mtk_dsi_mt8163(dsi)) {
  mtk_dsi_bridge_mode_set_legacy(bridge, mode, adjusted);
  return;
 }
 mutex_lock(&dsi->strict_lock);
 if (!dsi->strict_active && !dsi->strict_fault &&
     mtk_dsi_bridge_mode_valid(bridge, NULL, adjusted) == MODE_OK)
  drm_display_mode_to_videomode(adjusted, &dsi->vm);
 mutex_unlock(&dsi->strict_lock);
}
