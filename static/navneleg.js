var navneleg_activated = false;
var timoutInProgress = false;

function navneleg() {
    if (navneleg_activated) return;

    navneleg_activated = true;

    var tutorelements = document.getElementsByClassName('tutoraddress');
    var tutors = [];
    //Extracting all tutornames, aliases and images from the website
    for (var i = 0, l = tutorelements.length; i < l; ++i) {
        var tutor = tutorelements[i];
        var name = tutor.getElementsByClassName('name')[0].innerHTML.trim();
        var pic = tutor.getElementsByClassName('tutorpicture');
        var alias = name;
        
        //Remove the '"' from the alias if tutor has an alias
        if (tutor.getElementsByClassName('nickname').length > 0) {
            alias = tutor.getElementsByClassName('nickname')[0].innerHTML;
            alias = alias.substr(1, alias.length - 2);
        }

        //If tutor has an image add them to the game pool
        if (pic) {
            pic = pic[0].src;
            tutors.push({
                'name': name,
                'pic': pic,
                'alias': alias
            });
        }
    }

    var remainingTutors;
    var level = 1;

    //Used to add all tutors to the game again
    var reset_tutors = function reset_tutors() {
        remainingTutors = [];
        tutors.forEach(tutor => remainingTutors.push(tutor));
    };

    reset_tutors();

    //Find the art image hidden on the page and prepare for streak
    var arto = document.getElementById('arto');
    if (arto) document.body.appendChild(arto);
    var content = document.getElementById('content');
    content.innerHTML = '<h1>Navneleg<\/h1>\n' +
        '<p id="navneleg_stats"><\/p>\n' +
        '<p id="navneleg_status"><\/p>\n' +
        '<p id="navneleg_container" style="position: relative; height: 130px"> + ' +
        '<img style="max-width: 130px; max-height: 130px" id="navneleg_tutorpicture"><\/p>\n' +
        '<p><input id="navneleg_input"><\/p>\n' +
        '<p><input type="button" id="navneleg_submit" value="Indsend gæt"><\/p>\n';

    if (arto) {
        var container = document.getElementById('navneleg_container');
        arto.style.position = 'absolute';
        arto.style.left = arto.style.bottom = '5px';
        arto.style.opacity = '0.5';
        arto.style.display = 'none';
        container.appendChild(arto);
    }

    var currentIdx;
    var wins = 0,
        losses = 0,
        streak = 0;

    //Prepare needed document elements
    var stats = document.getElementById('navneleg_stats');
    var status = document.getElementById('navneleg_status');
    var pic = document.getElementById('navneleg_tutorpicture');
    var input = document.getElementById('navneleg_input');
    var submitButton = document.getElementById('navneleg_submit');

    var plural = function plural(n, noun) {
        if (n == 1) return n + " " + noun;
        else return n + " " + noun + "e";
    };

    var next_timer = null;

    var clear_next_timer = function clear_next_timer() {
        if (next_timer) {
            clearTimeout(next_timer);
            next_timer = null;
        }
    };

    var set_next_timer = function set_next_timer() {
            clear_next_timer();
            timoutInProgress = true;
            next_timer = setTimeout(next_tutor, 2000);
    };

    var submit = function submit() {
        if (!timoutInProgress) {
            var fullName = remainingTutors[currentIdx].name;
            var currentName = remainingTutors[currentIdx].name.replace(/ .*/, '');
            var als = remainingTutors[currentIdx].alias;
            var guess = input.value.toLowerCase();
            
            switch (guess) {
                case currentName.toLowerCase():
                case fullName.toLowerCase():
                case als.toLowerCase():
                    guessResponse(status, fullName, als, true);

                    remainingTutors.splice(currentIdx, 1);
                    
                    if (remainingTutors.length === 0) {
                        reset_tutors();
                        ++level;
                        status.innerHTML = "Welcome to experience level " + level + ".";
                    }
                    ++wins;
                    ++streak;
                    break;
                
                case 'jeppe' || 'henrijeppe':
                    status.innerHTML = "Korrekt! Ish...";
                    break;
                
                default:
                    let partOfName = false;
                    fullName.split(" ").forEach(s => {
                        if (guess == s.toLowerCase())
                            partOfName = true;
                    })

                    guessResponse(status, fullName, als, partOfName);

                    if (partOfName) {
                        ++wins;
                        ++streak;
                    } else {
                        ++losses;
                        streak = 0;
                    }
            }
            set_next_timer();
        }
    };

    submitButton.onclick = submit;

    var next_tutor = function next_tutor() {
        next_timer = null;
        currentIdx = Math.floor(Math.random() * remainingTutors.length);
        var t = remainingTutors[currentIdx];
        pic.src = t.pic;
        input.value = '';
        var statString = plural(wins, "korrekt") + ", " + plural(losses, "forkert");
        if (streak > 1) {
            statString += ", " + plural(streak, "korrekt") + " i streg";
        }
        stats.innerHTML = statString;
        var levelText = (level == 1) ? "" : (" (level " + level + ")");
        if (arto) {
            arto.style.display = (level == 1) ? "none" : "";
        }
        document.title = "Navneleg" + levelText + "! " + wins + "/" + losses + " (" + streak + ")";
        status.innerHTML = "Hvem er følgende tutor? Indtast fornavnet eller et kendt kaldenavn.";

        input.focus();
        timoutInProgress = false;
    };

    next_tutor();

    input.onkeydown = function(e) {
        if (next_timer == null && e.keyCode === 13) {
            submit();
        }
        e.stopPropagation();
    };

    var guessResponse = function guessResponse(status, fullName, als, correct) {
        let tmp = correct ? "Korrekt! Det fulde navn er " : "Nej, det var ";
        status.innerHTML =  tmp + fullName + (als.toLowerCase() === fullName.toLowerCase() ? "." : " og kaldenavn er " + als + ".");
    };

}

function win_key_down(e) {
    if (!e) e = window.event;
    if (e.keyCode === 78) {
        navneleg();
        e.preventDefault();
        return false;
    }
    return true;
}


window.addEventListener('keydown', win_key_down, false);