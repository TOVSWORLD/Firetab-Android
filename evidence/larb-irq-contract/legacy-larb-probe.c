{
	struct mtk_smi_larb *larbpriv;
	struct resource *res;
	struct device *dev = &pdev->dev;
	struct device_node *smi_node;
	struct platform_device *smi_pdev;
	int ret, larbid;

	if (!dev->pm_domain)
		return -EPROBE_DEFER;

	larbpriv = devm_kzalloc(dev, sizeof(*larbpriv), GFP_KERNEL);
	if (!larbpriv)
		return -ENOMEM;

	res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
	larbpriv->base = devm_ioremap_resource(dev, res);
	if (IS_ERR(larbpriv->base))
		return PTR_ERR(larbpriv->base);

	larbpriv->clk_apb = devm_clk_get(dev, "apb");
	if (IS_ERR(larbpriv->clk_apb))
		return PTR_ERR(larbpriv->clk_apb);

	larbpriv->clk_smi = devm_clk_get(dev, "smi");
	if (IS_ERR(larbpriv->clk_smi))
		return PTR_ERR(larbpriv->clk_smi);

	smi_node = of_parse_phandle(dev->of_node, "mediatek,smi", 0);
	if (!smi_node)
		return -EINVAL;

	ret = of_property_read_u32(dev->of_node, "mediatek,larbid", &larbid);
	if (ret)
		return ret;

	smi_pdev = of_find_device_by_node(smi_node);
	of_node_put(smi_node);
	if (smi_pdev) {
		larbpriv->smi = &smi_pdev->dev;
	} else {
		dev_err(dev, "Failed to get the smi_common device\n");
		return -EINVAL;
	}

	smi_data->larb_base[larbid] = (unsigned long)larbpriv->base;
	smi_data->larb[larbid] = dev;
	smi_data->larb_nr++;

	SMIMSG("larb %d-cnt %d probe done\n", larbid, smi_data->larb_nr);

	pm_runtime_enable(dev);
	dev_set_drvdata(dev, larbpriv);
	return 0;
}

static int mtk_smi_larb_remove(struct platform_device *pdev)
{
	pm_runtime_disable(&pdev->dev);
	return 0;
}

static const struct of_device_id mtk_smi_larb_of_ids[] = {
	{ .compatible = "mediatek,mt8173-smi-larb", },
	{ .compatible = "mediatek,mt8163-smi-larb", },
	{ .compatible = "mediatek,mt8127-smi-larb", },
	{}
};
