const confirmBtn = document.querySelector("#confirmBtn");
const getCatId = (id) => (confirmBtn.attributes.href.value = `/panel/remove_cat/${id}`);

$(document).ready(function () {

  $('#modalCenter').on('hidden.bs.modal', function () {
    $("#id_name").removeClass('border border-danger');
    $("#nameError").text('');
    $("#id_main").removeClass('border border-danger');
    $("#mainError").text('');
  });


  $(".remove-btn").click(function () {
    $("#notice").html("");
    const catType = $(this).attr("data-obj");
    if (catType === "main") {
      $("#notice").html(
        '<span class="mdi mdi-alert mdi-24px"></span>' +
          "در صورت حذف این موضوع اصلی همه موضوعات فرعی آن نیز حذف خواهند شد"
      );
    }
  });

  $("#create-btn").click(function () {
    $("#myForm").prop("action", "/panel/add_cat/");
    $("#myForm")[0].reset();
    $("#submit-btn").html("افزودن");
    $("#modalTitle").html("افزودن موضوع جدید");
  });

  $(".edit-btn").click(function () {
    const id = $(this).attr("data-obj");
    const url = `/panel/edit_cat/${id}/`;
    $("#myForm").prop("action", url);
    $("#submit-btn").html("ذخیره تغییرات");
    $("#modalTitle").html("ویرایش موضوع");

    $.ajax({
      type: "GET",
      url: $("#myForm").attr("action"),
      success: function (response) {
        if (response.is_subcat) $("#id_main").prop("disabled", false);
        $("#id_name").prop("value", response.name);
        $("#id_is_subcat").prop("checked", response.is_subcat);
        $("#id_main").prop("value", response.main);
      },
    });
  });

  $("#id_is_subcat").change(function () {
    if ($(this).is(":checked")) {
      $("#id_main").prop("disabled", false);
    } else {
      $("#id_main").prop("disabled", true);
      $("#mainError").html("");
      $("#id_main").removeClass("border-danger");
    }
  });

  $("#id_name").on("keydown", function () {
    $("#nameError").html("");
    $("#id_name").removeClass("border-danger");
  });

  $("#id_main").on("click", function () {
    $("#mainError").html("");
    $("#id_main").removeClass("border-danger");
  });

  $("#myForm").on("submit", function (event) {
    event.preventDefault();
    if ($(this).attr("action").includes("edit")) {
      const newName = $("#id_name").val();
      const newIsSubcat = $("#id_is_subcat").is(":checked");
      const newMain = $("#id_main").val();

      $.ajax({
        type: "POST",
        url: $(this).attr("action"),
        data: {
          name: newName,
          is_subcat: newIsSubcat,
          main: newMain,
          csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
          $("#nameError").html("");
          $("#mainError").html("");
          if (response.success) {
            $("#modalCenter").modal("hide");
            setTimeout(() => {
              Swal.fire({
                title: "موفقیت!",
                text: "موضوع جدید با موفقیت ویرایش شد",
                icon: "success",
                confirmButtonText: "باشه",
              }).then((result) => {
                if (result.isConfirmed) {
                  location.reload();
                }
              });
            }, 200);
          } else {
            $.each(response.errors, function (field, errors) {
              if (field === "name") {
                $("#nameError").append(errors);
                $("#id_name").addClass("border-danger");
              }

              if (field === "main") {
                $("#mainError").append(errors);
                $("#id_main").addClass("border-danger");
              }
            });
          }
        },
      });
    } else {
      $.ajax({
        type: "POST",
        url: $(this).attr("action"),
        data: $(this).serialize(),
        success: function (response) {
          $("#nameError").html("");
          $("#mainError").html("");
          if (response.success) {
            $("#modalCenter").modal("hide");
            setTimeout(() => {
              Swal.fire({
                title: "موفقیت!",
                text: "موضوع جدید با موفقیت اضافه شد",
                icon: "success",
                confirmButtonText: "باشه",
              }).then((result) => {
                if (result.isConfirmed) {
                  location.reload();
                }
              });
            }, 200);
          } else {
            $.each(response.errors, function (field, errors) {
              if (field === "name") {
                $("#nameError").append(errors);
                $("#id_name").addClass("border-danger");
              }

              if (field === "main") {
                $("#mainError").append(errors);
                $("#id_main").addClass("border-danger");
              }
            });
          }
        },
      });
    }
  });
});