import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

patch(ProductScreen.prototype, {
    get freshKeypadButtons() {
        return ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0", ".", "Enter"].map((value) => ({ value }));
    },
    freshKeypadClick(value) {
        if (value === "Enter") {
            this.numberBuffer.capture();
            this.numberBuffer.reset();
            return;
        }
        this.onNumpadClick(value);
    },
    async freshScan(event) {
        if (event.key !== "Enter") return;
        event.preventDefault();
        event.stopPropagation();
        const value = event.target.value.trim();
        if (!value || this.pos.freshQuickPaymentBusy) return;
        event.target.value = "";
        await this.barcodeReader.scan(value);
    },
    freshTogglePrint() {
        this.pos.config.iface_print_auto = !this.pos.config.iface_print_auto;
    },
    async fastValidate(paymentMethod) {
        const order = this.currentOrder;
        if (this.pos.freshQuickPaymentBusy || !order || order.state !== "draft" || order.isEmpty()) {
            return;
        }
        // Existing tender, refunds and terminal payments require the standard payment screen.
        // Never silently replace a partial payment or bypass its validation.
        if (
            order.payment_ids.length || order.isRefund || order.priceIncl <= 0 ||
            paymentMethod.payment_method_type !== "none" ||
            paymentMethod.type === "pay_later" ||
            !this.pos.config.fast_payment_method_ids.some((method) => method.id === paymentMethod.id)
        ) {
            return this.pos.pay();
        }
        this.pos.freshQuickPaymentBusy = true;
        try {
            return await super.fastValidate(paymentMethod);
        } finally {
            this.pos.freshQuickPaymentBusy = false;
        }
    },
});
