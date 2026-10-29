
	status = musb_platform_init(musb);
	/* pr_info("musb init controller after allocate\n"); */
#ifdef CONFIG_OF
	musb->xceiv->io_priv = ctrlp;
#endif
	musb_platform_enable(musb);
