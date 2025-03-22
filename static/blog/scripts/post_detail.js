$(document).ready(function () {
  get_like_count();
  $("#submit-btn").prop("disabled", true);

  $("#open-comment").click(function () {
    $("#comment-form").removeClass("d-none");
    $("#message").val("");
    $("#message").focus();
  });

  $("#cancel-btn").click(function () {
    $("#comment-form").addClass("d-none");
  });

  $("#message").on("keyup", function () {
    if ($(this).val().trim() === "") {
      $("#submit-btn").prop("disabled", true);
    } else {
      $("#submit-btn").prop("disabled", false);
    }
  });

  $(".open-answers").click(function () {
    const commentId = $(this).data("comment-id");
    $("#answers-" + commentId).toggleClass("d-none");
    $(this).find(".fas").toggleClass("fa-chevron-up fa-chevron-down");
  });

  $(".answer-btn").click(function () {
    const commentId = $(this).data("comment-id");
    const answerForm = $("#answer-form-" + commentId);
    $(".answer-form").addClass("d-none");
    $("#comment-form").addClass("d-none");
    answerForm.removeClass("d-none");
    if (answerForm.is(":visible")) {
      const textarea = answerForm.find("textarea");
      textarea.val("");
      textarea.focus();
    }
  });

  $(".answer-message").keyup(function () {
    if ($(this).val().trim() === "") {
      $(".submit-answer").prop("disabled", true);
    } else {
      $(".submit-answer").prop("disabled", false);
    }
  });

  $(".close-btn").click(function () {
    const commentId = $(this).data("comment-id");
    $("#answer-form-" + commentId).addClass("d-none");
  });

  $(".login-alert").click(function () {
    Swal.fire({
      title: "لطفا به حساب کاربری خود وارد شوید یا ثبت نام کنید",
      icon: "warning",
      showCloseButton: true,
      showConfirmButton: false,
      html: `
            <a href="{% url 'login' %}" class="btn btn-secondary">
                <i class="fas fa-sign-in-alt"></i>
                ورود
            </a>
            <a href="{% url 'register' %}" class="btn btn-info">
                <i class="fas fa-user-plus"></i>
                ثبت نام
            </a>
        `,
    });
  });

  $(".answer-form").submit(function (event) {
    event.preventDefault();
    $.ajax({
      type: "POST",
      url: $(this).attr("action"),
      data: $(this).serialize(),
      success: function (response) {
        if (response.success) {
          Swal.fire({
            title: "",
            text: 
            response.has_perm ? "نظر شما با موفقیت ارسال شد"
            : "نظر شما با موفقیت ارسال شد و پس از تایید ادمین در سایت قرار خواهد گرفت",
            icon: "success",
            confirmButtonText: "باشه",
          }).then((result) => {
            if (result.isConfirmed) {
              $(".answer-form").addClass("d-none");
              location.reload();
            }
          });
        } else {
          Swal.fire({
            title: "خطا!",
            text: "نظر شما ارسال نشد",
            icon: "error",
            confirmButtonText: "باشه",
          }).then((result) => {
            if (result.isConfirmed) {
              $(".answer-form").addClass("d-none");
            }
          });
        }
      },
    });
  });

  $("#comment-form").on("submit", function (event) {
    event.preventDefault();
    $.ajax({
      type: "POST",
      url: $(this).attr("action"),
      data: $(this).serialize(),
      success: function (response) {
        if (response.success) {
          Swal.fire({
            title: "",
            text: 
            response.has_perm ? "نظر شما با موفقیت ارسال شد"
            : "نظر شما با موفقیت ارسال شد و پس از تایید ادمین در سایت قرار خواهد گرفت",
            icon: "success",
            confirmButtonText: "باشه",
          }).then((result) => {
            if (result.isConfirmed) {
              $("#comment-form").addClass("d-none");
              location.reload();
            }
          });
        } else {
          Swal.fire({
            title: "خطا!",
            text: "نظر شما ارسال نشد",
            icon: "error",
            confirmButtonText: "باشه",
          }).then((result) => {
            if (result.isConfirmed) {
              $("#comment-form").addClass("d-none");
            }
          });
        }
      },
    });
  });
});
