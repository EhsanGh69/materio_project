$(document).ready(function(){
    $("#search-user").keyup(function(){
        $("#reciever_err").text('');
        $("#reciever-input").val("");
        $("#message").val("");
        if($(this).val())
            search_user($(this).val())
        else
            $('#search-result').html("")  
    })

    // event delegation: used for elements loaded by ajax 
    $(document).on("click", ".user-reciever", function(){
        $("#reciever_err").text('');
        let box = $(this).find(".reciever-box");
        let icon = $(this).find(".check-icon");
        let reciever = $(this).find(".reciever-username")

        if (box.hasClass("bg-light")) {
            box.removeClass("bg-light");
            icon.addClass("d-none");
            $("#reciever-input").val("");
        } else {
            $(".reciever-box").removeClass("bg-light");
            $(".check-icon").addClass("d-none");
            
            box.addClass("bg-light");
            icon.removeClass("d-none");
            $("#reciever-input").val(reciever.data("username"));
        }
    })

    $('#modalCenter').on('hidden.bs.modal', function () {
        $("#reciever_err").text('');
        $("#subject_err").text('');
        $("#message_err").text('');
        $("#subject").removeClass('border border-danger');
        $("#message").removeClass('border border-danger');
    });

    $("#subject").keyup(function(){
        $(this).removeClass('border border-danger');
        $("#subject_err").text('');
    })

    $("#message").keyup(function(){
        $(this).removeClass('border border-danger');
        $("#message_err").text('');
    })

    $('#seen-btn').click(function(e){
        $(this).removeClass('btn-outline-success')
        $(this).addClass('btn-success')
        $('#unseen-btn').removeClass('btn-secondary')
        $('#unseen-btn').addClass('btn-outline-secondary')
        setTimeout(() => {
            e.preventDefault()
            load_notifs('seen', 1)
        }, 200)
    })

    $('#unseen-btn').click(function(e){
        $(this).removeClass('btn-outline-secondary')
        $(this).addClass('btn-secondary')
        $('#seen-btn').removeClass('btn-success')
        $('#seen-btn').addClass('btn-outline-success')
        setTimeout(() => {
            e.preventDefault()
            load_notifs('unseen', 1)
        }, 200)
    })
})