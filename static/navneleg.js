var navneleg_activated = false;
var YEAR = 2014;
function P(year, name) {
  var rel = (YEAR - 2000) - year;
  var prefix = ['', 'g', 'b', 'o', 't'];
  if (rel < prefix.length) return prefix[rel] + name;
  else return 't' + (rel - 3) + name;
}
function navneleg() {
  if (navneleg_activated) return;
  navneleg_activated = true;

  var aliases = {
    "Amalie Louise Stokholm":             ["fust"],
    "Anders Grøn Stensgaard":             ["grøn"],
    "Andreas Bendix Nuppenau":            ["funu"],
    "Asbjørn Stensgaard Nielsen":         ["funi"],
    "Asger Holm Agergaard":               ["fugr"],
    "Astrid Christiansen":                ["fuis"],
    "Benedikte Sofie Werk":               ["fubi"],
    "Camilla Ulbæk Pedersen":             ['fuul', P(14, 'sekr')],
    "Casper Grønne Christensen":          ["grønne"],
    "Christian Bonar Zeuthen":            ["fuzu", "zeuthen"],
    "Christina Gøttsche":                 ["gøttsche", "mullemus", "gotye"],
    "Christina Moeslund Madsen":          ["fuhr"],
    "Daniel Holst Hviid":                 ["hviid", "minihahn", "mini-hahn", "mini hahn"],
    "Frederik Brinck Truelsen":           ["ålen"],
    "Frederik Jerløv":                    ["furi"],
    "Hans Christian Tankred":             ["hc"],
    "Hans-Martin Hannibal Lauridsen":     ["hannibal"],
    "Henrik Knakkegaard Christensen":     ["knakke", "kendrik", "kenrik"],
    "Henrik Lund Mortensen":              ["fuan"],
    "Jacob Albæk Schnedler":              ["fuco", P(14, 'nf')],
    "Jakob Grünewald Hjørringgaard":      ["gotye"],
    "Jakob Rørsted Mosumgaard":           [P(12, "sekr"), "fuan", "lokalemus"],
    "Jakob Ørhøj":                        ["ørhøj"],
    "Jens Ager Sørensen":                 ["printer jens"],
    "Johan Johannes Johannessen":         ["3j", "triple j", "triple-j", "jjj"],
    "Jonas Termansen":                    ["sortie", "sortiecat", "sortie@cs.au.dk", "sortie@maxsi.org"],
    "Kasper Lynderup Jensen":             ["jomfru jensen"],
    "Katrin Debes Kristensen":            ["solmor"],
    "Kenneth Lund Kjærgaard":             ["smør", 'gris',],
    "Knud Valdemar Trøllund Lassen":      ["kv", 'knude', 'knude vertex'],
    "Kristoffer Winge":                   [P(10, "pr"), "fuan", "winge", "vinge"],
    "Lasse Ellegaard Jørgensen":          ["nano-peter"],
    "Lauge Hoyer":                        ["gefuit", "burløs"],
    "Mads Fabricius":                     [P(12, "cerm"), "trefuan"],
    "Mai Olsen":                          ['3. mai'],
    "Maiken Haahr Hansen":                [P(11, "vc"), "fuma", "mølle"],
    "Malene Machon Pedersen":             ["machon"],
    "Marianne Ostenfeldt Mortensen":      ["fumo"],
    "Marie Ulsø":                         ["øko", "økomor", "kromutter", "ulsø"],
    "Martin Sand":                        ["furt", P(14, 'form')],
    "Mathias Dannesbo":                   ["fuhi", P(13, 'vc')],
    "Mathias Jaquet Mavraganis":          ["tform", "mavraganis", "tantra", P(14, 'kass')],
    "Mathias Rav":                        [P(13, "form"), "rav", "not so much", "webfar", "webtumling", "webbaby", 'webtween', 'webteen', 'webmathias'],
    "Mette Lysgaard Schulz":              [P(13, "pr"), "metten", "koorbaby"],
    "Mette Galsgaard Malle":              ['biomalle', 'malle'],
    "Morten Henriksen Birk":              ["birk", 'brik'],
    "Nick Bakkegaard":                    ["justin", "bieber", "justin bieber", "web", "webfar"],
    "Niclas Spas Sørensen":               ["spas"],
    "Oliver Emil Harritslev Christensen": ["fuet", 'efuit'],
    "Peter Lystlund Matzen":              ["matzen", "grisefar"],
    "Philip Tchernavskij":                ["tchernavskij", "mini-sean", "mini sean", "minisean", "gefuit"],
    "Sabrina Tang Christensen":           [P(11, "cerm")],
    "Sandra Bleuenn Picard S Pedersen":   ["fubs"],
    "Sofie Filskov Hermansen":            ['ælling 1']
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
