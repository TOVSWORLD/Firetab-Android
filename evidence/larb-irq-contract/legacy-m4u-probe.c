
static int m4u_probe(struct platform_device *pdev)
{
	struct device_node *node = pdev->dev.of_node;
	int ret;

	if (pdev->dev.of_node) {
		ret = of_property_read_u32(node, "cell-index", &pdev->id);
		if (ret)
			M4UMSG("[DTS] get m4u platform_device id fail!!\n");
	}
	M4UINFO("m4u_probe 1, pdev id = %d name = %s\n", pdev->id, pdev->name);

	gM4uDev->pDev[pdev->id] = &pdev->dev;
	gM4uDev->m4u_base[pdev->id] = (unsigned long)of_iomap(node, 0);
	gM4uDev->irq_num[pdev->id] = irq_of_parse_and_map(node, 0);

	M4UINFO("m4u_probe 2, of_iomap: 0x%lx, irq_num: %d, pDev: %p\n",
		gM4uDev->m4u_base[pdev->id], gM4uDev->irq_num[pdev->id], gM4uDev->pDev[pdev->id]);

	if (0 == pdev->id) {
		m4u_domain_init(gM4uDev, &gMvaNode_unknown);
