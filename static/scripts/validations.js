$(document).ready(function(){
    // $('#controlledDiabetes').hide();
    // $('#conthypertension').hide(); 
    $('#controlledDiabetes').addClass("hidden");
    $('#conthypertension').addClass("hidden");

    $('#yeshyper').change(function(){
        // $('#conthypertension').toggleClass("hidden");
        if(this.checked){
            $('#conthypertension').removeClass("hidden");
        }
        else {
            $('#conthypertension').addClass("hidden");
        }
    });

    $('#yesdia').change(function(){
        if(this.checked){
            $('#controlledDiabetes').removeClass("hidden");
        }
        else{
            $('#controlledDiabetes').addClass("hidden");
        }
    });


    $('#btn').click(function(){
        let flag = false;

        let pwcheck = $('#pw1').val() == $('#pw2').val();

        if (!pwcheck) {
            $('#pwcheck').text("Password doesn't match!");
            flag = true
        }
        else {
            $('#pwcheck').text("");
        }

        if($('#bd').val()){

            // let bdcheck = /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test($('#bd').val());
            let bdcheck = /^\d{4}-\d{2}-\d{2}$/.test($('#bd').val());

            if (!bdcheck) {
                $('#bdcheck').text("Wrong Format");
                flag = true
            }
            else {
                $('#bdcheck').text("");
            }
        }

        if(!flag){
            $(this).attr("type","submit");
        }
    });

    $('#btn2').click(function(){
        
        let pwcheck = $('#pw1').val() == $('#pw2').val();

        if (!pwcheck) {
            $('#pwcheck').text("Password doesn't match!");
        }
        else {
            $('#pwcheck').text("");
        }

        if(pwcheck){
            $(this).attr("type","submit");
        }
    });

});