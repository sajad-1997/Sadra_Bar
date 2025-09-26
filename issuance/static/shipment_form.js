document.addEventListener('DOMContentLoaded', function () {

    // تابع کمک برای انتخاب فیلدهای prefix=shipment
    function getShipmentField(name) {
        return document.querySelector(`[name="shipment-${name}"]`);
    }

    const valueField = getShipmentField("value");
    const insuranceField = getShipmentField("insurance");
    const loadingFeeField = getShipmentField("loading_fee");
    const totalFareField = getShipmentField("total_fare");
    const freightField = getShipmentField("freight");

    if (!valueField || !insuranceField || !loadingFeeField || !totalFareField || !freightField) {
        console.warn("یکی از فیلدهای فرم پیدا نشد!");
        return;
    }

    // 🟢 تبدیل اعداد فارسی/عربی به انگلیسی
    function toEnglishNumber(str) {
        if (!str) return "";
        return str
            .replace(/[\u06F0-\u06F9]/g, d => String.fromCharCode(d.charCodeAt(0) - 1728))
            .replace(/[\u0660-\u0669]/g, d => String.fromCharCode(d.charCodeAt(0) - 1584));
    }

    // 🟢 تبدیل رشته به عدد خالص (ریال)
    function parseNumber(value) {
        if (!value) return 0;
        value = toEnglishNumber(value.toString());
        const num = Number(value.replace(/,/g, ""));
        return isNaN(num) ? 0 : num;
    }

    // 🟢 اضافه کردن جداکننده سه‌تایی
    function formatNumber(num) {
        if (isNaN(num)) return "0";
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    // 🟢 بروزرسانی بیمه (۱۰٪ value)
    function updateInsurance() {
        const value = parseNumber(valueField.value);
        const insurance = Math.round(value * 0.001);
        insuranceField.value = formatNumber(insurance);
    }

    // 🟢 بروزرسانی کرایه خالص (freight)
    function updateFreight() {
        const totalFare = parseNumber(totalFareField.value);
        const insurance = parseNumber(insuranceField.value);
        const loadingFee = parseNumber(loadingFeeField.value);

        let freight = totalFare - (insurance + loadingFee);
        if (isNaN(freight) || freight < 0) freight = 0;

        freightField.value = formatNumber(freight);
    }

    // 🟢 اتصال رویداد input به فیلدها و محاسبه خودکار
    function attachField(field, callback) {
        field.addEventListener("input", function () {
            const cursorPos = field.selectionStart;
            const rawValue = parseNumber(field.value);
            field.value = formatNumber(rawValue);
            field.setSelectionRange(cursorPos, cursorPos);

            if (callback) callback();
        });
    }

    // اتصال رویدادها
    attachField(valueField, () => { updateInsurance(); updateFreight(); });
    attachField(insuranceField, updateFreight);
    attachField(loadingFeeField, updateFreight);
    attachField(totalFareField, updateFreight);

    // 🟢 مقداردهی اولیه و فرمت
    [valueField, insuranceField, loadingFeeField, totalFareField, freightField].forEach(field => {
        if (field && field.value) {
            field.value = formatNumber(parseNumber(field.value));
        }
    });

    // 🟢 محاسبه اولیه بیمه و کرایه
    updateInsurance();
    updateFreight();
});
