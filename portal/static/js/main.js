$("#nonPrintedFilterBtn").click(function() {
    $("#printedFilterBtn").removeClass("tz-singlebtn-active");
    $("#nonPrintedFilterBtn").addClass("tz-singlebtn-active");
    $(".printed").show();
    $(".non-printed").hide()
});
$("#printedFilterBtn").click(function() {
    $("#nonPrintedFilterBtn").removeClass("tz-singlebtn-active");
    $("#printedFilterBtn").addClass("tz-singlebtn-active");
    $(".non-printed").show();
    $(".printed").hide()
});
var pages;
var bw_rate;
var color_rate;
$('#fileForm').submit(function(e) {
    document.querySelector("#progressContainer").style.display = "block";
    e.preventDefault();
    $form = $(this);
    var formData = new FormData(this);
    $("#transactionFormDiv").hide().trigger("reset");
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: formData,
        success: function(response) {
            $('.error').remove();
            console.log(response);
            if (response.error) {
                formError(response.message);
                $.each(response.errors, function(name, error) {
                    error = '<small class="text-muted error">' + error + '</small>';
                    $form.find('[name=' + name + ']').after(error)
                })
            } else {
                $("#transactionForm").attr("action", ("/transactions/add/" + response.file_uuid + "/"));
                $('#preview-btn').attr("fileUrl", response.file_url);
                $("#transactionFormDiv").show();
                pages = response.pages;
                blackWhite = response.bw_rate;
                bw_rate = response.bw_rate;
                color_rate = response.color_rate;
                calculateForm()
            }
        },
        xhr: function() {
            var xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener("progress", function(event) {
                var loaded = event.loaded / 1000000;
                loaded = loaded.toFixed(2);
                var total = event.total / 1000000;
                total = total.toFixed(2);
                var percent = (event.loaded / event.total) * 100;
                document.getElementById("progressBar").value = Math.round(percent);
                document.getElementById("status").innerHTML = Math.round(percent) + "% uploaded...(" + loaded + " mb/" + total + " mb)"
            }, !1);
            xhr.addEventListener("load", function(event) {
                document.getElementById("status").innerHTML = event.target.responseText;
                document.getElementById("progressBar").value = 100;
                document.querySelector("#progressContainer").style.display = "none"
            }, !1);
            xhr.addEventListener("error", function(event) {
                document.getElementById("status").innerHTML = "Upload Failed";
                document.querySelector("#progressContainer").style.display = "none"
            }, !1);
            xhr.addEventListener("abort", function(event) {
                document.getElementById("status").innerHTML = "Upload Aborted";
                document.querySelector("#progressContainer").style.display = "none"
            }, !1);
            return xhr
        },
        cache: !1,
        contentType: !1,
        processData: !1
    })
});

function fileChange() {
    var allowed_types = ["jpg", "pdf", "png", "jpeg"];
    var input_field = document.querySelector("#file");
    file_name = input_field.files[0].name;
    if (allowed_types.includes(file_name.slice(file_name.lastIndexOf('.') + 1, ))) {
        $("#formErrorMessage").hide().text("");
        $("#file-input-msg").text(input_field.files[0].name);
        document.querySelector('#change').innerHTML = "Change";
        $("#transactionForm").show()
    } else {
        $("#transactionForm").trigger("reset").hide();
        $("#fileForm").trigger("reset");
        $("#file-input-msg").text("Choose File");
        document.querySelector('#change').innerHTML = "Upload";
        $("#formErrorMessage").show().text("File Type Not Allowed");
        document.querySelector('.text-muted-error').style.display = "none"
    }
    $("#fileForm").trigger("submit")
}

function calculateForm() {
    var copies = document.querySelector("#copies").value;
    copies = Math.floor(copies);
    if (copies < 1) {
        copies = 1
    }
    document.querySelector("#copies").value = copies;
    var rate;
    if (document.querySelector('#color').checked) {
        rate = color_rate
    } else {
        rate = bw_rate
    }
    document.querySelector("#pages").innerHTML = pages;
    var amount = pages * rate * copies;
    document.querySelector("#amount").innerHTML = amount;
    console.log(userBalance);
    if (userBalance < amount) {
        $("#coin-label").trigger("click");
        $("#wallet").attr('disabled', 'disabled');
        $('#wallet-label').removeAttr('onclick');
        $('#wallet-label').addClass('tz-disabled-label')
    } else {
        $("#wallet-label").attr('onclick', 'paymentClassChange(this.id)');
        $('#wallet').removeAttr('disabled');
        $('#wallet-label').removeClass('tz-disabled-label')
    }
}

function preview() {
    if (document.querySelector('#file').files[0]) {
        if (document.querySelector('#preview-btn').hasAttribute('fileurl')) {
            let url = document.querySelector('#preview-btn').getAttribute('fileurl');
            $("#canvas-container").show();
            previewpdf(url)
        }
    } else {
        document.querySelector('#preview-btn').removeAttribute('fileurl');
        $("#canvas-container").hide()
    }
}
$("#previewmodal").on('shown.bs.modal', function() {
    if (document.querySelector('#preview-btn').hasAttribute('fileurl')) {} else {
        $("#previewmodal").modal('hide')
    }
});
let pdfDoc, pageNum, pageIsRendering, pageNumIsPending, scale, canvas, ctx;
let canvasCount = 0;

function getCanvasElement() {
    let container = document.querySelector('#canvas-container');
    let canvas = document.createElement("canvas");
    let id;
    if (canvasCount == 0) {
        canvasCount++
    } else {
        id = "my-canvas" + canvasCount;
        let removingElement = document.getElementById(id);
        container.removeChild(removingElement);
        canvasCount++
    }
    id = "my-canvas" + canvasCount;
    canvas.setAttribute("id", id);
    container.appendChild(canvas);
    return (id)
}

function previewpdf(data) {
    pdfDoc = null, pageNum = 1, pageIsRendering = !1, pageNumIsPending = null, scale = 1;
    let id = getCanvasElement();
    canvas = document.getElementById(id), ctx = canvas.getContext('2d');
    pdfjsLib.getDocument(data).promise.then(pdfDoc_ => {
        pdfDoc = pdfDoc_;
        document.querySelector('#page-count').textContent = pdfDoc.numPages;
        renderPage(pageNum)
    })
}
const renderPage = num => {
    pageIsRendering = !0;
    pdfDoc.getPage(num).then(page => {
        document.querySelector("#previewmodal").style.display = "block";
        let container = document.querySelector('#canvas-container');
        let viewport = page.getViewport(1);
        scale = container.clientWidth / viewport.width;
        viewport = page.getViewport(scale);
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        const renderCtx = {
            canvasContext: ctx,
            viewport
        }
        page.render(renderCtx).promise.then(() => {
            pageIsRendering = !1;
            if (pageNumIsPending !== null) {
                renderPage(pageNumIsPending);
                pageNumIsPending = null
            }
        });
        document.querySelector('#page-num').textContent = num
    })
};
const queueRenderPage = num => {
    if (pageIsRendering) {
        pageNumIsPending = num
    } else {
        renderPage(num)
    }
}
const showPrevPage = () => {
    if (pageNum <= 1) {
        return
    }
    pageNum--;
    queueRenderPage(pageNum)
}
const showNextPage = () => {
    if (pageNum >= pdfDoc.numPages) {
        return
    }
    pageNum++;
    queueRenderPage(pageNum)
}
document.querySelector('#prev').addEventListener('click', showPrevPage);
document.querySelector('#next').addEventListener('click', showNextPage);

function formError(error_message) {
    $("#fileForm").trigger("reset");
    $("#file-input-msg").text("Choose File");
    $("#formErrorMessage").show().text(error_message)
}

function currentlink(element) {
    defaultlink();
    document.getElementById(element).classList.add("tz-currentlink");
    document.getElementById("forget-section").style.display = "none";
    if (element == 'login-tab') {
        document.getElementById("login-section").style.display = "block";
        document.getElementById("sign-up-section").style.display = "none"
    } else {
        document.getElementById("sign-up-section").style.display = "block";
        document.getElementById("login-section").style.display = "none"
    }
}

function defaultlink() {
    var check = document.getElementById("login-tab").classList.contains("tz-currentlink");
    if (check == !0) {
        document.getElementById("login-tab").classList.remove("tz-currentlink")
    }
    check = document.getElementById("sign-up-tab").classList.contains("tz-currentlink");
    if (check == !0) {
        document.getElementById("sign-up-tab").classList.remove("tz-currentlink")
    }
}

function forgetPassword(element) {
    defaultlink();
    document.getElementById("sign-up-section").style.display = "none";
    document.getElementById("login-section").style.display = "none";
    document.getElementById("forget-section").style.display = "block"
}

function copiesChange(o) {
    var copies = document.querySelector("#copies");
    var c = -(-copies.value);
    if (o == "+") {
        copies.value = c + 1
    } else {
        if (c > 1) {
            copies.value = c - 1
        }
    }
    calculateForm()
}

function colorModeClassChange(id) {
    if (id == "color-label") {
        $("#black-white").attr("checked", false);
        $("#color").attr("checked", true);
        document.querySelector("#color-label").classList.add("tz-radio-label-active");
        document.querySelector("#black-white-label").classList.remove("tz-radio-label-active")
    } else {
        $("#color").attr("checked", false);
        $("#black-white").attr("checked", true);
        document.querySelector("#black-white-label").classList.add("tz-radio-label-active");
        document.querySelector("#color-label").classList.remove("tz-radio-label-active")
    }
}

function paymentClassChange(id) {
    if (id == "wallet-label") {
        $("#coin").attr("checked", false);
        $("#wallet").attr("checked", true);
        document.querySelector("#wallet-label").classList.add("tz-radio-label-active");
        document.querySelector("#coin-label").classList.remove("tz-radio-label-active")
    } else {
        $("#wallet").attr("checked", false);
        $("#coin").attr("checked", true);
        document.querySelector("#coin-label").classList.add("tz-radio-label-active");
        document.querySelector("#wallet-label").classList.remove("tz-radio-label-active")
    }
}