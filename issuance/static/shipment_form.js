// ================================================
// shipment.js - نسخه بهینه و آماده برای فایل خارجی
// ================================================

// -----------------------------
// ۱. تبدیل اعداد فارسی/عربی و جداکننده سه‌تایی
// -----------------------------
function toEnglishNumber(str) {
    if (!str) return "";
    return str
        .replace(/[\u06F0-\u06F9]/g, d => String.fromCharCode(d.charCodeAt(0) - 1728))
        .replace(/[\u0660-\u0669]/g, d => String.fromCharCode(d.charCodeAt(0) - 1584));
}

function parseNumber(value) {
    if (!value) return 0;
    value = toEnglishNumber(value.toString());
    const num = Number(value.replace(/,/g, ""));
    return isNaN(num) ? 0 : num;
}

function formatNumber(num) {
    if (isNaN(num)) return "0";
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// -----------------------------
// ۲. اعمال جداکننده سه‌تایی روی فیلد عددی با حفظ کرسر
// -----------------------------
function attachNumericField(field, callback) {
    field.addEventListener("input", function () {
        let cursorPos = field.selectionStart;
        let originalLength = field.value.length;
        let rawValue = parseNumber(field.value);
        field.value = formatNumber(rawValue);
        let newLength = field.value.length;
        cursorPos += newLength - originalLength;
        field.setSelectionRange(cursorPos, cursorPos);
        if (callback) callback();
    });
}

// -----------------------------
// ۳. محاسبات بارنامه
// -----------------------------
function initShipmentCalculations() {
    function getField(name) {
        return document.querySelector(`[name="shipment-${name}"]`);
    }

    const valueField = getField("value");
    const insuranceField = getField("insurance");
    const loadingFeeField = getField("loading_fee");
    const totalFareField = getField("total_fare");
    const freightField = getField("freight");

    if (!valueField || !insuranceField || !loadingFeeField || !totalFareField || !freightField) {
        console.warn("یکی از فیلدهای فرم پیدا نشد!");
        return;
    }

    function updateInsurance() {
        const value = parseNumber(valueField.value);
        let insurance = 0;
        if (value > 0) {
            if (value <= 2000000000) {
                insurance = 2000000;  // سقف تا ۲ میلیارد → بیمه ثابت
            } else {
                insurance = Math.floor(value * 0.001);  // بالای ۲ میلیارد → ۱۰ درصد
            }
        }
        // const insurance = Math.round(value * 0.001);
        insuranceField.value = formatNumber(insurance);
    }

    function updateFreight() {
        const totalFare = parseNumber(totalFareField.value);
        const insurance = parseNumber(insuranceField.value);
        const loadingFee = parseNumber(loadingFeeField.value);
        let freight = totalFare - (insurance + loadingFee);
        if (isNaN(freight) || freight < 0) freight = 0;
        freightField.value = formatNumber(freight);
    }

    [valueField, insuranceField, loadingFeeField, totalFareField].forEach(f => {
        attachNumericField(f, () => {
            updateInsurance();
            updateFreight();
        });
    });

    attachNumericField(freightField);

    // مقداردهی اولیه
    [valueField, insuranceField, loadingFeeField, totalFareField, freightField].forEach(f => {
        if (f.value) f.value = formatNumber(parseNumber(f.value));
    });
    updateInsurance();
    updateFreight();
}

// -----------------------------
// ۴. selectable-card toggle
// -----------------------------
function initSelectableCards() {
    document.querySelectorAll('.selectable-card').forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        if (!checkbox) return;
        if (checkbox.checked) card.classList.add('selected');
        card.addEventListener('click', e => {
            if (e.target.tagName === 'INPUT') return; // جلوگیری از toggle روی input داخلی
            checkbox.checked = !checkbox.checked;
            card.classList.toggle('selected', checkbox.checked);
        });
    });
}

// -----------------------------
// ۵. توضیحات انتخابی + دستی (نسخه اصلاح‌شده - toggle قابل لغو)
// -----------------------------
function initExplanations() {
    const select = document.getElementById("explanations");
    const customInput = document.getElementById("customExplanation");
    const previewBox = document.getElementById("finalExplanationsPreview");
    const hiddenSelected = document.getElementById("selectedExplanations");
    const hiddenCustom = document.getElementById("customExplanations");

    if (!select || !previewBox || !hiddenSelected || !hiddenCustom) return;

    function updatePreview() {
        const selectedOptions = Array.from(select.options)
            .filter(opt => opt.selected)
            .map(opt => opt.value);

        const customLines = (customInput ? customInput.value : "")
            .split("\n")
            .map(l => l.trim())
            .filter(l => l);

        let html = "<ul>";
        selectedOptions.forEach(item => {
            html += `<li>${item}</li>`;
        });
        customLines.forEach(item => {
            html += `<li>${item}</li>`;
        });
        html += "</ul>";

        previewBox.innerHTML = html;
        hiddenSelected.value = JSON.stringify(selectedOptions);
        hiddenCustom.value = JSON.stringify(customLines);
    }

    // برای هر گزینه: mousedown (اصلی) + fallback click/touchstart
    Array.from(select.options).forEach(opt => {
        const toggleHandler = function (e) {
            // جلوگیری از رفتار پیش‌فرض مرورگر تا بتوانیم selection را خودمان مدیریت کنیم
            e.preventDefault();

            const willSelect = !this.selected;

            if (willSelect) {
                // اگر قرار است انتخاب شود => بقیه را پاک کن تا رفتار تک‌انتخابی حفظ شود
                Array.from(select.options).forEach(o => o.selected = false);
                this.selected = true;
            } else {
                // اگر قرار است لغو شود => خودش را false کن (بدون انتخاب هیچ‌کسی)
                this.selected = false;
            }

            updatePreview();
            return false;
        };

        opt.addEventListener('mousedown', toggleHandler);
        opt.addEventListener('click', toggleHandler);            // fallback برای برخی مرورگرها
        opt.addEventListener('touchstart', function (e) {         // موبایل: جلوگیری از native picker در برخی پیاده‌سازی‌ها
            // توجه: touchstart باید passive:false باشد تا preventDefault کار کند؛
            // اگر مرورگر اجازه نده، ممکن است native picker باز شود — در آن صورت باید از UI دلخواه استفاده کنید.
            e.preventDefault();
            toggleHandler.call(this, e);
        }, {passive: false});
    });

    // پشتیبانی ساده از صفحه‌کلید: Space/Enter برای toggle روی گزینهٔ فعلی
    select.addEventListener('keydown', function (e) {
        if (e.key === ' ' || e.key === 'Enter') {
            e.preventDefault();
            const idx = select.selectedIndex;
            if (idx >= 0) {
                const opt = select.options[idx];
                const willSelect = !opt.selected;
                if (willSelect) {
                    Array.from(select.options).forEach(o => o.selected = false);
                    opt.selected = true;
                } else {
                    opt.selected = false;
                }
                updatePreview();
            }
        }
    });

    if (customInput) {
        customInput.addEventListener('input', updatePreview);
    }

    // مقداردهی اولیه
    updatePreview();
}


// -----------------------------
// ۶. جستجوی AJAX
// -----------------------------
function enableSearch(inputId, resultsId, hiddenId, searchUrl, extraOptions = {}) {
    const $input = $(`#${inputId}`);
    const $results = $(`#${resultsId}`);
    const $hidden = $(`#${hiddenId}`);

    $input.on('keyup', function () {
        let query = $input.val().trim();
        if (query.length === 0) {
            $results.empty().hide();
            return;
        }

        $.ajax({
            url: searchUrl,
            data: {q: query},
            success: function (data) {
                let html = "";
                if (data.results.length > 0) {
                    data.results.forEach(item => {
                        html += `<button type="button"
                                        class="list-group-item list-group-item-action"
                                        data-id="${item.id}"
                                        data-name="${item.name}"
                                        data-phone="${item.phone || ''}"
                                        data-plate="${item.plate || ''}">
                                        <strong>${item.name}</strong>
                                        ${item.phone ? " - " + item.phone : ""}
                                 </button>`;
                    });
                } else {
                    html = `<div class="list-group-item">نتیجه‌ای یافت نشد!!!</div>`;
                }
                $results.html(html).show();
            }
        });
    });

    $(document).on('click', `#${resultsId} .list-group-item`, function () {
        const $item = $(this);
        const id = $item.data('id');
        const name = $item.data('name');
        const plate = $item.data('plate');

        $input.val(name);
        $hidden.val(id);

        if (extraOptions.fillPlateField && plate !== undefined) {
            $(`#${extraOptions.fillPlateField}`).val(plate);
        }

        $results.empty().hide();

        if (extraOptions.updateVehicleAjax) {
            $.ajax({
                url: extraOptions.updateVehicleAjax,
                data: {driver_id: id},
                success: function (res) {
                    if (res.success) {
                        $("#first-number").text(res.vehicle.two_digit);
                        $("#letter").text(res.vehicle.alphabet);
                        $("#second-number").text(res.vehicle.three_digit);
                        $("#province").text(res.vehicle.series);
                    } else {
                        $("#first-number").text("--");
                        $("#letter").text("-");
                        $("#second-number").text("---");
                        $("#province").text("**");
                    }
                }
            });
        }
    });
}

// -----------------------------
// ۷. اجرا در بارگذاری DOM
// -----------------------------
document.addEventListener("DOMContentLoaded", function () {
    initShipmentCalculations();
    initSelectableCards();
    initExplanations();

    // فعال‌سازی search AJAX با URL هایی که از template ارسال شدن
    enableSearch("receiver-input", "receiver-results", "receiver-id", urls.searchCustomer);
    enableSearch("sender-input", "sender-results", "sender-id", urls.searchCustomer);
    enableSearch("driver-input", "driver-results", "driver-id", urls.searchDriver, {
        fillPlateField: "vehicle-plate",
        updateVehicleAjax: urls.getVehicleByDriver
    });
    enableSearch("vehicle-input", "vehicle-results", "vehicle-id", urls.searchVehicle);
});
