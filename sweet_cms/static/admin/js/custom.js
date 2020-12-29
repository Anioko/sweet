$('.swal-confirm').click(function(){
    let bulk = $(this).hasClass('swal-confirm-bulk');
    if (bulk){
        let ids = $("input[name='ids[]']").val();
        if (ids == ""){
            swal({
                title: "Nothing Selected?",
                text: "There are no elements selected",
                icon: "info",
            });
            return false;
        }
    }
    let warn = $(this).attr('swal-warn');
    let e = this;
    swal({
        title: "Are you sure?",
        text: warn + "\n\nOnce done, this action cannot be reverted",
        icon: "warning",
        buttons: true,
        dangerMode: true,
    })
        .then((willDelete) => {
            if (willDelete) {
                let form = $(e).next($('form.swal-submit'));
                form.submit();
            } else {
                return false;
            }
        });
    return false;
});
$('.bulk-checkbox').click(function (){
    let val = $(this).attr('data-value');
    let inp = $(this).prev($('#checkbox-'+val));
    let ids = $("input[name='ids[]']");
    let vals = ids.val();
    if (vals != ""){
        vals = vals.split(',');
    }
    else {
        vals = [];
    }
    if (vals.constructor !== Array){
        vals = [vals];
    }
    if (! inp[0].checked){
        if (!(vals.includes(""+val))){
            vals.push(val);
        }
    }
    else {
        if (vals.includes(val)){
            vals = vals.filter((value, index, arr) => {return parseInt(value) != parseInt(val);});
        }
    }
    ids.val(vals);
});
$(document).on('change', 'input[type=date]', function () {
    const target = $(this);
    const e = target.parents('form').find('input:hidden[name=offset]');
    let offset = new Date().getTimezoneOffset();
    e.val(offset);
});
$(document).on('change', 'input[type="datetime-local"]', function () {
    const target = $(this);
    const e = target.parents('form').find('input:hidden[name=offset]');
    let offset = new Date().getTimezoneOffset();
    e.val(offset);
});
function adjustForTimezone(date){
    var timeOffsetInMS = date.getTimezoneOffset() * 60000;
    let result_date = new Date();
    result_date.setTime(date.getTime() - timeOffsetInMS);
    return result_date;
}
function changeTimeInputsToLocal(){
    $('input[type="datetime-local"]').each(function(){
       let utc_date = $(this).val();
       utc_date = new Date(utc_date);
       let d = new Date();
       d.setTime(utc_date.getTime() - utc_date.getTimezoneOffset() * 60000);
       // console.log(result, result.getTime(), utc_date.getTime());
        // yyyy-MM-ddThh:mm
        const result_str = ("0" + d.getFullYear()).slice(-4) + "-" + ("0"+(d.getMonth()+1)).slice(-2) + "-" +
            ("0" + d.getDate()).slice(-2) + "T" + ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
       $(this).val(result_str);
    });
}
