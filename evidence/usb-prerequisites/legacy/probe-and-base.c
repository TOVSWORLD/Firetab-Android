 * bridge to a platform device; this driver then suffices.
 */
static int musb_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	int irq = 0;
	int status;
	void __iomem *base;
#ifdef CONFIG_OF
	void __iomem *pbase;
	unsigned long usb_mac_base;
	unsigned long usb_phy_base;

	pr_info("musb probe\n");
	DBG(0, "musb_removed to 0\n");
	musb_removed = 0;
	if (dts_np) {
		DBG(0, "dts node from dts_np\n");
		pdev->dev.of_node = dts_np;
	} else {
		DBG(0, "dts node from of_find_compatible_node\n");
		pdev->dev.of_node = of_find_compatible_node(NULL, NULL, "mediatek,USB0");
	}
	if (pdev->dev.of_node == NULL)
		pr_info("USB get node failed\n");
	base = of_iomap(pdev->dev.of_node, 0);
	usb_irq_number = irq_of_parse_and_map(pdev->dev.of_node, 0);
	pbase = of_iomap(pdev->dev.of_node, 1);

	usb_mac_base = (unsigned long)base;
	usb_phy_base = (unsigned long)pbase;
	irq = usb_irq_number;
	pr_info("musb probe reg: 0x%lx ,0x%lx , irq: 0x%d\n", usb_mac_base, usb_phy_base,
		usb_irq_number);
#endif
#ifdef CONFIG_OF
	status = musb_init_controller(dev, irq, base, pbase);
#else
	base = (void *)USB_BASE;
	status = musb_init_controller(dev, irq, base);
