window.addEventListener("load",function(){
  function c(e){
    e.querySelectorAll(".remove").forEach(function(e){
      e.addEventListener("click",function(){
        this.parentNode.remove()
      })
    })
  }
  document.querySelectorAll(".dynamic-array-widget").forEach(function(i){
    c(i),i.querySelector(".add-array-item").addEventListener("click",function(){
      var e, t, n;
      e = i.querySelector(".array-item");
      t = e.cloneNode(!0);
      r = t.querySelector("input").getAttribute("id").split("_");
      n = r.slice(0,-1).join("_")+"_"+String(parseInt(r.slice(-1)[0])+1);
      t.querySelector("input").setAttribute("id",n);
      t.querySelector("input").value = "";
      t.querySelector("label").remove();
      t.querySelector(".remove").style.display = "inherit";
      c(t);
      e.parentElement.appendChild(t);
    })
  })
});

$(function () {
  $('#two-columns-forms-second .col-md-7').attr("class", "col-md-12");
  $('#two-columns-forms-second .col-md-5').attr("class", "col-md-12");
  ['#div_id_work_plan', '#div_id_mech_to_fix', '#div_id_mech_plan',
  '#div_id_penalties', '#div_id_encouragement'].forEach(function (item) {
    $(item).attr("class", "form-group row md-form");
  })

  var reportDate = $('input[name=report_date]')
  reportDate.after(`<span><b>${reportDate.val()}</b></span>`);
  reportDate.hide();
  reportDate.parent().css({'textAlign': 'center'});

  $('label.col-md-12').each(function (index) {
    clone = $(this).clone();
    clone.attr("for", `${clone.attr("for")}_0`);
    $(this).parent().find("ul li:first-child input").before(clone);
    $(this).parent().find("ul li:first-child .remove").hide();
    $(this).remove();
  });

  $('.add-array-item').addClass('btn btn-outline-default waves-effect btn-sm').text("ДОБАВИТЬ ЕЩЕ");
});
