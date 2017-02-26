var navneleg_activated = false;
var YEAR = 2016;
function P(year, name) {
  var age = (YEAR - 2000) - year;
  var prefix = ['', 'g', 'b', 'o', 'to'];
  if (age < prefix.length) return prefix[age] + name;
  else return 't' + (age - 3) + 'o' + name;
}
function navneleg() {
  if (navneleg_activated) return;
  navneleg_activated = true;

  var aliases = {
    "Alexandra Aldershaab Hou Olsen":     ["webfar"],  
    "Amalie Louise Stokholm":             ["fust"],
    "Anders Grøn Stensgaard":             ["grøn"],
    "Andreas Bendix Nuppenau":            ["funu"],
    "Asbjørn Stensgaard Nielsen":         ["funi"],
    "Asger Holm Agergaard":               ["fugr"],
    "Astrid Christiansen":                ["fuis"],
    "Benedikte Sofie Werk":               ["fubi"],
    "Burmor":                             ["morten", "morten kaj", "morten kaj degnebolig", "burfar"],
    "Camilla Ulbæk Pedersen":             ['fuul', P(14, 'sekr')],
    "Casper Grønne Christensen":          ["grønne"],
    "Christian Bonar Zeuthen":            ["fuzu", "zeuthen"],
    "Christian Engelbrecht Larsen":       ["gris", "grisen"],
    "Christina Gøttsche":                 ["gøttsche", "mullemus", "gotye"],
    "Christina Moeslund Madsen":          ["fuhr"],
    "Daniel Holst Hviid":                 ["hviid", "minihahn", "mini-hahn", "mini hahn"],
    "Emma Hillgaard":                     ['ælling 2'],
    "Esben Bo Mahler":                    ["humanist esben", "humanist", "esben humaniora"],
    "Frederik Brinck Truelsen":           ["ålen"],
    "Frederik Jerløv":                    ["furi"],
    "Freja Frederikke Pinderup":          ["fupi"],
    "Hans Christian Tankred":             ["hc"],
    "Hans-Martin Hannibal Lauridsen":     ["hannibal"],
    "Henrik Knakkegaard Christensen":     ["knakke", "kendrik", "kenrik"],
    "Henrik Lund Mortensen":              ["fuan"],
    "Jacob Albæk Schnedler":              ["fuco", P(14, 'nf')],
    "Jakob Grünewald Hjørringgaard":      ["gotye"],
    "Jakob Rørsted Mosumgaard":           [P(12, "sekr"), "fuan", "lokalemus"],
    "Jakob Ørhøj":                        ["ørhøj"],
    "Janne Højmark Mønster":              [P(15, "sekr")],
    "Jens Ager Sørensen":                 ["printer jens"],
    "Johan Johannes Johannessen":         ["3j", "triple j", "triple-j", "jjj"],
    "Jonas Termansen":                    ["sortie", "sortiecat", "sortie@cs.au.dk", "sortie@maxsi.org"],
    "Julie Thiim Gadeberg":               ["fuji"],
    "Kasper Lynderup Jensen":             ["jomfru jensen"],
    "Katrin Debes Kristensen":            ["solmor"],
    "Kenneth Lund Kjærgaard":             ["smør", 'gris',],
    "Klaus Skovgaard Olesen":             ["kalus"],
    "Knud Valdemar Trøllund Lassen":      ["kv", 'knude', 'knude vertex'],
    "Kristoffer Winge":                   [P(10, "pr"), "fuan", "winge", "vinge"],
    "Lasse Ellegaard Jørgensen":          ["nano-peter"],
    "Lauge Hoyer":                        ["gefuit", "burløs"],
    "Laura Patricia Kaplan":              ["lokalemis","lokalemiss"],
    "Mads Fabricius":                     [P(12, "cerm"), "trefuan"],
    "Mai Olsen":                          ['3. mai'],
    "Maija Bindzus":                      ['øko'],
    "Maiken Haahr Hansen":                [P(11, "vc"), "fuma", "mølle"],
    "Malene Machon Pedersen":             ["machon"],
    "Marianne Ostenfeldt Mortensen":      ["fumo"],
    "Marie Louisa Tølbøll Berthelsen":    ["marie louisa", "burmor"],
    "Marie Ulsø":                         ["øko", "økomor", "kromutter", "ulsø"],
    "Martin Sand":                        ["furt", P(14, 'form')],
    "Mathias Dannesbo":                   ["fuhi", P(13, 'vc')],
    "Mathias Jaquet Mavraganis":          ["tform", "mavraganis", "tantra", P(14, 'kass')],
    "Mathias Rav":                        [P(13, "form"), "rav", "webfar", "webtumling", "webbaby", 'webtween', 'webteen', 'webmathias', 'amber'],
    "Mette Lysgaard Schulz":              [P(13, "pr"), "metten", "koorbaby"],
    "Mette Galsgaard Malle":              ['biomalle', 'malle','øko the outlaw malle - crusher of lions'],
    "Morten Henriksen Birk":              ["birk", 'brik'],
    "Morten Stockmarr Liljegren":         ["blomsterpenis","kone-laura", "tform", "tutorform", "formand", "form"],
    "Nguyen Thien Anh Ly":                ["an", "anh", "ann"],
    "Nick Bakkegaard":                    ["justin", "bieber", "justin bieber", "web", "webfar"],
    "Niclas Spas Sørensen":               ["spas"],
    "Nikolai Houlberg Øllegaard":         ["webfar"],
    "Nikolaj Voetmann Bruun":             ["bruun"],
    "Oliver Emil Harritslev Christensen": ["fuet", 'efuit'],
    "Per Næsby Høgfeldt":                 [P(15, "fuan")],
    "Peter Lystlund Matzen":              ["matzen", "grisefar"],
    "Philip Tchernavskij":                ["tchernavskij", "mini-sean", "mini sean", "minisean", "gefuit"],
    "Rune Terp":                          ['sten', 'runesten'],
    "Sabrina Tang Christensen":           [P(11, "cerm")],
    "Sandra Bleuenn Picard S Pedersen":   ["fubs"],
    "Sofie Filskov Hermansen":            ['ælling 1'],
    "Thomas Skovlund Hansen":             ['fuve'],
    "Tobias Svangtun Nowak":              ['toby', 'fucktoby', '#fucktoby'],
    "Tómas Bragi Reynisson":		      ["tomas"] 
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
