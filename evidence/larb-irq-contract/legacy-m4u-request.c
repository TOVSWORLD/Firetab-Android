
	pM4URegBackUp = kmalloc(M4U_REG_BACKUP_SIZE * TOTAL_M4U_NUM, GFP_KERNEL | __GFP_ZERO);
	if (pM4URegBackUp == NULL) {
		M4UMSG("Physical memory not available size=%d.\n", (int)M4U_REG_BACKUP_SIZE);
		return -1;
	}

	spin_lock_init(&gM4u_reg_lock);

	m4u_reg_init(&gM4uDomain, ProtectPA, m4u_id);

	if (request_irq(m4u_dev->irq_num[m4u_id], MTK_M4U_isr, IRQF_TRIGGER_LOW, "m4u", NULL)) {
		M4UERR("request M4U%d IRQ line failed\n", m4u_id);
		return -ENODEV;
	}
	M4UINFO("request_irq, irq_num=%d\n", m4u_dev->irq_num[m4u_id]);

	m4u_isr_pause_timer_init();

