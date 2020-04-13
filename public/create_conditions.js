/*
Ensures balanced random assignment to two conditions.
To trigger, nav to app/create_conditions.html
If conditions list exists, will display
Else, type in desired # of participants per condition, and click 'Generate Conditions'
Will generate conditions and participant index, stored in Firebase
*/

// access and get a reference to the Firebase database service
var db = firebase.database();
var ref = db.ref('conditions');

// Fisher-Yates (aka Knuth) Shuffle (https://github.com/coolaj86/knuth-shuffle)
function shuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex;
  // While there remain elements to shuffle...
  while (currentIndex > 0) {
    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex --;
    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }
  return array;
}

// When you start a new study, create the conditions in the db, start the participant index at 0
function createConditions() {
  var n = parseInt($("#nparticipants").val()),
    controlArray = Array(n).fill(0),
    exptArray = Array(n).fill(1),
    conditionsArray = shuffle(controlArray.concat(exptArray));

  db.ref('conditions/').set({
    conditionsArray: conditionsArray,
    participantIndex: 0
  });
}

ref.on("value", function(snapshot) {
  var val = snapshot.val();
  if (val) {
    $("#conditionsArray").html(val.conditionsArray);
    $("#participantIndex").html(val.participantIndex);
  } else {
    $("#conditionsArray").html("None");
    $("#participantIndex").html("None");
  }
});

