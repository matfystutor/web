$(document).ready(function() {
    // Set the navbar position as absolute when viewing images. This prevents
    // the navbar from obscuring the image when using pinch to zoom.
    $(".navbar-fixed-top").css("position", "absolute");

    // Get array of all slugs
    var slugs = $("#tkgal-container > *").map(function() {
        return $(this).attr("data-permlink");
    }).get();

    // Call changeCurrent on click on the controls
    $(".tkgal-control").click(function(e) {
        e.preventDefault();
        pauseMedia();
        changeCurrent($(this).attr("href"));
    });


    function changeCurrent(newimage) {
        // Calculate prev and next images
        var l = slugs.length;
        var i = slugs.indexOf(newimage);
        var prev = slugs[(((i-1)%l)+l)%l]; // mod is broken for negative numbers
        var next = slugs[(i+1)%l];

        // Update visibility of current picture
        $("#tkgal-container>*").addClass("hidden");
        $("#tkgal-caption-container>*").addClass("hidden");
        $("[data-permlink='"+newimage+"']").removeClass("hidden");

        function deferMedia(file) {
            // This removes the data- prefix from 'file' causing the browser to
            // request the files.
            var img = $("[data-permlink='"+file+"'] [data-src]");

            if(img.attr('data-srcset')){
                img.attr('srcset', img.attr('data-srcset'));
                img.removeAttr('data-srcset');
            }
            if(img.attr('data-sizes')){
                img.attr('sizes', img.attr('data-sizes'));
                img.removeAttr('data-sizes');
            }
            if(img.attr('data-src')){
                img.attr('src', img.attr('data-src'));
                img.removeAttr('data-src');
            }
        }
        deferMedia(prev);
        deferMedia(next);

        // Rewrite history
        window.history.replaceState(null, null, newimage + location.search);
    }

    // Call swipehandler on swipe
    // This requires jquery touchswipe
  $("body").swipe( { // register swipe anywhere in body
        swipeLeft:swipehandler,
        swipeRight:swipehandler,
        allowPageScroll:"auto",
        fingers:1
  });

    function swipehandler(event, direction) {
        switch(direction) {
        case "left":
            $(".tkgal-next:visible").eq(0).click();
            break;
        case "right":
            $(".tkgal-prev:visible").eq(0).click();
            break;
        default:
        }
    }

  //Load neighbors on pageload
  loadfirst = $("#tkgal-container > :not(.hidden)").attr("data-permlink");
  changeCurrent(loadfirst);
});

function pauseMedia() {
    $("video, audio").each(function(){
        $(this).get(0).pause();
    });
}

function togglePlay() {
    $(":not(.hidden) > * > audio, :not(.hidden) > * > video").each(function(){
        if (this.paused ? this.play() : this.pause());
    });
}

// simulate link press when arrow keys are pressed
$(document).keydown(function(e) {
    switch(e.which) {
    case 37: // left
        $(".tkgal-prev:visible").eq(0).click();
        break;
    case 39: // right
        $(".tkgal-next:visible").eq(0).click();
        break;
    case 32: // space
        togglePlay();
        if(e.target == document.body) {
            e.preventDefault();
        }
        break;
    case 27: // ESC
        $("#albumlink").eq(0).click();
        if(e.target == document.body) {
            e.preventDefault();
        }
        break;
    }
});

$('video').click(function(){ togglePlay(); });
