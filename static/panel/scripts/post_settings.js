function get_related_tags(id){
    $.ajax({
        url: `/panel/get_related_tags/${id}`,
        success: function(data){
            if (data.length > 0){
                let btns = ''
                $.each(data, function(index, item) {
                    btns += `<b class="badge bg-label-secondary me-2"># ${item}</b>`;
                });
                $("#tags-box").removeClass('d-none')
                $("#tags-items").html(btns)
            }
        }
    })
}

$(document).ready(function(){

    $('#modalCenter').on('hidden.bs.modal', function () {
        $("#tag_name_input").removeClass('border border-danger');
        $("#tag_name_err").text('');
    });

    $("#reject-btn").click(function(){
        $(this).addClass('d-none')
        $("#remove-btn").removeClass('d-none')
        $("#reason-box").removeClass('d-none')
        $("#send-btn-icon").removeClass('mdi-file-document-remove-outline')
        $("#send-btn-icon").addClass('mdi-file-document-alert-outline')
        $(".send-btn").removeClass('btn-danger')
        $(".send-btn").addClass('btn-warning')
        $("#send-btn-txt").text('ارسال و رد پست')
    })

    $("#remove-btn").click(function(){
        $(this).addClass('d-none')
        $("#reject-btn").removeClass('d-none')
        $("#reason-box").removeClass('d-none')
        $("#send-btn-icon").addClass('mdi-file-document-remove-outline')
        $(".send-btn").addClass('btn-danger')
        $("#send-btn-txt").text('ارسال و حذف پست')
    })

    $(".cancel-btn").click(function(){
        $('#reason-report').text('')
        $("#reason-box").addClass('d-none')
        $("#remove-btn").removeClass('d-none')
        $("#reject-btn").removeClass('d-none')
    })

    $("#main_cat").change(function (){
        if($(this).val() !== "") {
            $.ajax({
                url: `/panel/get_sub_cats/${$(this).val()}`,
                success: function(data){
                    let options = '<option value="">انتخاب کنید</option>';
                    $.each(data, function(index, item) {
                        options += 
                        `<option value="${item.id}">
                            ${item.name}
                        </option>`;
                    });
                    $("#sub_cat").html(options).prop("disabled", false)
                    get_related_tags($("#main_cat").val());
                }
            })
        }else{
            $("#sub_cat").html('<option value="">انتخاب کنید</option>').prop("disabled", true)
            $("#tags-box").addClass('d-none')
        }
    })

    $(".remove_tag_btn").click(function () {
        $("#removed_tag").text($(this).data("tag"))
    });

    $("#tag_name_input").keyup(function(){
        $(this).removeClass("border border-danger")
        $("#tag_name_err").text('')
    })

    $("#tag_form").submit(function (event) {
        event.preventDefault();
        $.ajax({
          type: "POST",
          url: $(this).attr("action"),
          data: $(this).serialize(),
          success: function (response) {
            if(response.success){
                $("#modalCenter").modal("hide");
                location.reload()
            }
            else {
              $("#tag_name_input").addClass("border border-danger")
              $("#tag_name_err").text(response.error)
            }
          },
        });
    });

    $("#confirm-btn").click(function(){
        $("#settings-form").submit()
    })

    $("#settings-form").submit(function (event) {
        event.preventDefault();
        $.ajax({
          type: "POST",
          url: $(this).attr("action"),
          data: $(this).serialize(),
          success: function (response) {
            if(response.success){
                window.location.href = response.redirect_url
            }
            else{
                $("#main_cat_err").text(response.errors.main_cat_err);
                $("#study_time_err").text(response.errors.study_time_err);
            }
          },
        });
    });
})