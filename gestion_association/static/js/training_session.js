$("#trainingForm").on("change", "*", function (event) {
  var champ_educateur = ["trainer_person", "type_training"];
  if (champ_educateur.indexOf(event.target.name) != -1) {
    var url = $("#trainingForm").data("seance-price-url");
    $.post(url, $("#trainingForm").serialize(), function (data) {
      $("#id_amount").val(data["montant_seance"]);
    });
  }
});