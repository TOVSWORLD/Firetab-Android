#ifndef CONFIG_MTK_CLKMGR
	usbpll_clk = devm_clk_get(&pdev->dev, "usbpll");
	if (IS_ERR(usbpll_clk)) {
		DBG(0, KERN_WARNING "cannot get usbpll clock\n");
		return PTR_ERR(usbpll_clk);
	}
	DBG(0, KERN_WARNING "get usbpll clock ok, prepare it\n");
	retval = clk_prepare(usbpll_clk);
	if (retval == 0) {
		DBG(0, KERN_WARNING "prepare done\n");
	} else {
		DBG(0, KERN_WARNING "prepare fail\n");
		return retval;
	}

	usb_clk = devm_clk_get(&pdev->dev, "usb");
	if (IS_ERR(usb_clk)) {
		DBG(0, KERN_WARNING "cannot get usb clock\n");
		return PTR_ERR(usb_clk);
	}
	DBG(0, KERN_WARNING "get usb clock ok, prepare it\n");
	retval = clk_prepare(usb_clk);
	if (retval == 0) {
		DBG(0, KERN_WARNING "prepare done\n");
	} else {
		DBG(0, KERN_WARNING "prepare fail\n");
		return retval;
	}

	usbmcu_clk = devm_clk_get(&pdev->dev, "usbmcu");
	if (IS_ERR(usbmcu_clk)) {
		DBG(0, KERN_WARNING "cannot get usbmcu clock\n");
		return PTR_ERR(usbmcu_clk);
	}
	DBG(0, KERN_WARNING "get usbmcu clock ok, prepare it\n");
	retval = clk_prepare(usbmcu_clk);
	if (retval == 0) {
		DBG(0, KERN_WARNING "prepare done\n");
	} else {
		DBG(0, KERN_WARNING "prepare fail\n");
		return retval;
	}

	icusb_clk = devm_clk_get(&pdev->dev, "icusb");
	if (IS_ERR(icusb_clk)) {
		DBG(0, KERN_WARNING "cannot get icusb clock\n");
		return PTR_ERR(icusb_clk);
	}
	DBG(0, KERN_WARNING "get icusb clock ok, prepare it\n");
	retval = clk_prepare(icusb_clk);
	if (retval == 0) {
		DBG(0, KERN_WARNING "prepare done\n");
	} else {
		DBG(0, KERN_WARNING "prepare fail\n");
		return retval;
	}
#endif

	mt_usb_device.dev.of_node = pdev->dev.of_node;
