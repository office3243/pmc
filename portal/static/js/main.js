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
window.addEventListener("load", function() {
    const loader = document.querySelector(".loader");
    loader.className += " hidden"
});
var pages;
var bw_rate;
var color_rate;
$('#fileForm').submit(function(e) {
    $("#processMessage").show();
    e.preventDefault();
    $form = $(this);
    var formData = new FormData(this);
    $("#transactionFormDiv").hide().trigger("reset");
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: formData,
        success: function(response) {
            $("#processMessage").hide();
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
        cache: !1,
        contentType: !1,
        processData: !1
    })
});

function fileChange() {
    var allowed_types = ["jpg", "pdf", "png"];
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
    var rate;
    if (document.querySelector('#color').checked) {
        rate = color_rate
    } else {
        rate = bw_rate
    }
    document.querySelector("#pages").innerHTML = pages;
    document.querySelector("#amount").innerHTML = pages * rate * copies
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