static void mt_usb_enable(struct musb *musb)
{
	unsigned long   flags;

	DBG(0, "%d, %d\n", mtk_usb_power, musb->power);

	if (musb->power == true)
		return;

	flags = musb_readl(musb->mregs, USB_L1INTM);

	/* mask ID pin, so "open clock" and "set flag" won't be interrupted. ISR may call clock_disable.*/
	musb_writel(mtk_musb->mregs, USB_L1INTM, (~IDDIG_INT_STATUS) & flags);

	/* Mark by ALPS01262215
	if (platform_init_first) {
		DBG(0,"usb init first\n\r");
		musb->is_host = true;
	} */

	if (!mtk_usb_power) {
		if (down_interruptible(&power_clock_lock))
			DBG(0, "USB20: %s: busy, Couldn't get power_clock_lock\n", __func__);

#ifndef FPGA_PLATFORM
		/*enable_pll(UNIVPLL, "USB_PLL");*/
		DBG(0, "enable UPLL before connect\n");
#endif
		mdelay(10);

		usb_phy_recover();

		mtk_usb_power = true;

		up(&power_clock_lock);
	}
	musb->power = true;

	musb_writel(mtk_musb->mregs, USB_L1INTM, flags);
}
