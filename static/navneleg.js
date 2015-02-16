var navneleg_activated = false;
function navneleg() {
  if (navneleg_activated) return;
  navneleg_activated = true;

  var aliases = {
	 "Anders Grøn Stensgaard" :				["grøn"],
	 "Hans-Martin Hannibal Lauridsen":		["hannibal"],
	 "Malene Machon Pedersen":					["machon"],
    "Andreas Bendix Nuppenau":            ["funu"],
    "Asbjørn Stensgaard Nielsen":         ["funi"],
    "Britt Fredsgaard":                   ["bkass", "bka$$", "fredslund", "fulu"],
    "Camilla Ulbæk Pedersen":             ['fuul'],
    "Casper Grønne Christensen":          ["grønne"],
    "Christian Bonar Zeuthen":            ["fuzu", "zeuthen"],
    "Christina Gøttsche":                 ["gøttsche", "mullemus", "gotye"],
    "Daniel Holst Hviid":                 ["hviid", "minihahn", "mini-hahn", "mini hahn"],
    "Frederik Brinck Truelsen":           ["ålen"],
    "Frederik Jerløv":                    ["furi"],
    "Hans Christian Tankred":             ["hc"],
    "Henrik Knakkegaard Christensen":     ["knakke", "kendrik", "kenrik"],
    "Henrik Lund Mortensen":              ["fuan"],
    "Jacob Albæk Schnedler":              ["fuco"],
    "Jakob Grünewald Hjørringgaard":      ["gotye"],
    "Jakob Rørsted Mosumgaard":           ["gsekr", "fuan", "lokalemus"],
    "Jakob Ørhøj":                        ["ørhøj"],
    "Johan Johannes Johannessen":         ["3j", "triple j", "triple-j", "jjj"],
    "Jonas Termansen":                    ["sortie", "sortiecat", "sortie@cs.au.dk", "sortie@maxsi.org"],
    "Kasper Lynderup Jensen":             ["jomfru jensen"],
    "Katrin Debes Kristensen":            ["solmor"],
    "Kenneth Lund Kjærgaard":             ["smør"],
    "Knud Valdemar Trøllund Lassen":      ["kv"],
    "Kristoffer Winge":                   ["opr", "fuan", "winge", "vinge"],
    "Lasse Ellegaard Jørgensen":          ["nano-peter"],
    "Lauge Hoyer":                        ["gefuit", "burløs"],
    "Line Bjerg Sørensen":                ["fuli"],
    "Mads Fabricius":                     ["gcerm", "trefuan"],
    "Mai Olsen":                          ['3. mai'],
    "Maiken Haahr Hansen":                ["gvc", "fuma", "mølle"],
    "Marianne Ostenfeldt Mortensen":      ["fumo"],
    "Marie Ulsø":                         ["øko", "økomor", "kromutter", "ulsø"],
    "Martin Sand":                        ["furt"],
    "Mathias Dannesbo":                   ["fuhi"],
    "Mathias Jaquet Mavraganis":          ["tform", "mavraganis", "tantra"],
    "Mathias Rav":                        ["form", "rav", "not so much", "webfar", "webtumling", "webbaby"],
    "Mette Lysgaard Schulz":              ["pr", "metten", "koorbaby"],
    "Morten Henriksen Birk":              ["birk"],
    "Nick Bakkegaard":                    ["justin", "bieber", "justin bieber", "web", "webfar"],
    "Niclas Spas Sørensen":               ["spas"],
    "Peter Lystlund Matzen":              ["matzen", "grisefar"],
    "Philip Tchernavskij":                ["tchernavskij", "mini-sean", "mini sean", "minisean", "efuit"],
    "Sabrina Tang Christensen":           ["bcerm"],
    "Sandra Bleuenn Picard S Pedersen":   ["fubs"]
    //"Alexandra Fogtmann-Schulz":        ["tform"],
    //"Anne Nielsen":                     "",
    //"Diana Christensen":                "",
    //"Maja Harborg Slot":                "",
    //"Mette Bjerre":                     "",
    //"Signe Greve":                      "",
    //"Simon Aagaard Enni":               "",
  };

  var tutorelements = document.getElementsByClassName('tutoraddress');
  var tutors = [];
  for (var i = 0, l = tutorelements.length; i < l; ++i) {
    var e = tutorelements[i];
    var name = e.getElementsByClassName('name')[0].innerHTML.replace(/^[ \t\n\r]+|[ \t\n\r]+$/g, '');
    var pic = e.getElementsByClassName('tutorpicture');
    if (pic.length == 0) continue;
    pic = pic[0].src;
    tutors.push({'name': name, 'pic': pic});
  }

  var remainingTutors;
  var level = 1;

  var reset_tutors = function reset_tutors() {
    remainingTutors = [];
    for (var i = 0, l = tutors.length; i < l; ++i) {
      remainingTutors.push(tutors[i]);
    }
  };

  reset_tutors();

  var content = document.getElementById('content');
  content.innerHTML = '<h1>Navneleg<\/h1>\n'+
  '<p id="navneleg_stats"><\/p>\n'+
  '<p id="navneleg_status"><\/p>\n'+
  '<p style="height: 300px"><img style="max-width: 300px; max-height: 300px" id="navneleg_tutorpicture"><\/p>\n'+
  '<p><input id="navneleg_input"><\/p>\n'+
  '<p><input type="button" id="navneleg_submit" value="Indsend gæt"><\/p>\n'
  ;

  var currentIdx;
  var wins = 0, losses = 0, streak = 0;

  var stats = document.getElementById('navneleg_stats');
  var status = document.getElementById('navneleg_status');
  var pic = document.getElementById('navneleg_tutorpicture');
  var input = document.getElementById('navneleg_input');
  var submitButton = document.getElementById('navneleg_submit');

  var plural = function plural(n, noun) {
    if (n == 1) return n+" "+noun;
    else return n+" "+noun+"e";
  };

  var next_timer = null;

  var next_tutor = function next_tutor() {
    next_timer = null;
    currentIdx = Math.floor(Math.random()*remainingTutors.length);
    var t = remainingTutors[currentIdx];
    pic.src = t.pic;
    input.value = '';
    var statString = plural(wins, "korrekt")+", "+plural(losses, "forkert");
    if (streak > 1) {
      statString += ", "+plural(streak, "korrekt")+" i streg";
    }
    stats.innerHTML = statString;
    var levelText = (level == 1) ? "" : (" (level "+level+")");
    document.title = "Navneleg"+levelText+"! "+wins+"/"+losses+" ("+streak+")";
    status.innerHTML = "Hvem er følgende tutor? Indtast fornavnet eller et kendt kaldenavn.";
    input.focus();
  };

  var clear_next_timer = function clear_next_timer() {
    if (next_timer) {
      clearTimeout(next_timer);
      next_timer = null;
    }
  };
  var set_next_timer = function set_next_timer() {
    clear_next_timer();
    next_timer = setTimeout(next_tutor, 2000);
  };
  var submit = function submit() {
    var fullName = remainingTutors[currentIdx].name;
    var currentName = remainingTutors[currentIdx].name.replace(/ .*/, '');
    var als = aliases[fullName] ? aliases[fullName] : [];
    var guess = input.value.toLowerCase();
    if (guess == currentName.toLowerCase() || als.indexOf(guess) != -1) {
      status.innerHTML = "Korrekt! Det fulde navn er "+remainingTutors[currentIdx].name+".";
      remainingTutors.splice(currentIdx, 1);
      if (remainingTutors.length == 0) {
        reset_tutors();
        ++level;
        status.innerHTML = "Welcome to experience level "+level+".";
      }
      ++wins;
      ++streak;
    } else if (guess == 'jeppe' || guess == 'henrijeppe') {
      status.innerHTML = "Korrekt! Ish...";
    } else {
      status.innerHTML = "Nej, det var "+remainingTutors[currentIdx].name+".";
      ++losses;
      streak = 0;
    }
    set_next_timer();
  };
  submitButton.onclick = submit;
  next_tutor();

  var input_key_down = function input_key_down(e) {
    if (next_timer == null && e.keyCode == 13) {
      submit();
    }
    e.stopPropagation();
  };
  input.onkeydown = input_key_down;
}

function win_key_down(e) {
  if (!e) e = window.event;
  if (e.keyCode == 78) {
    navneleg();
    e.preventDefault();
    return false;
  }
  return true;
}
window.addEventListener('keydown', win_key_down, false);
