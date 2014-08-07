"use strict";

window.rthing = (function() {
    var rthing = {};
    
    $(document).ready(function() {
        // Put up with IE10
        if(/*@cc_on!@*/false) {
            $("body").addClass("ie10");
        }
        
        // Expand/hide button
        var expandImgLeft = $(".expand-img").css("left");
        var sidebarWidth = $(".sidebar").css("width");
        $(".expand-img").click(function(e) {
            if($(this).data("open")) {
                $(this).data("open", false);
                $(this).attr("src", rthingAssets.close_menu);
                $(this).animate({"left":expandImgLeft});
                $(this).parents(".sidebar").animate({"width":sidebarWidth});
                $(this).parents(".sidebar").children().not(this).animate({"opacity":1.0});
                
            }else{
                $(this).data("open", true);
                $(this).attr("src", rthingAssets.open_menu);
                $(this).animate({"left":3});
                $(this).parents(".sidebar").animate({"width":16});
                $(this).parents(".sidebar").children().not(this).animate({"opacity":0.0});
            }
        });
        
        // Compare order values
        // Positive if a > b, negative if a < b, 0 if a == b
        var compareOrder = function(a, b) {
            var a = (""+a).split("-");
            var b = (""+b).split("-");
            
            if(+a[0] > +b[0]) return 1;
            if(+a[0] < +b[0]) return -1;
            if(b.length < 2 && a.length == 2) return 1; // 0-0 > 0
            if(b.length == 2 && a.length < 2) return -1;
            if(+a[1] > +b[1]) return 1;
            if(+a[1] < +b[1]) return -1;
            return 0;
        }
        
        // Check if the first parts are equal; 0-1 = 0-0 = 0 != 1-0
        var firstEqual = function(a, b) {
            var a = (""+a).split("-");
            var b = (""+b).split("-");
            
            return a[0] == b[0];
        };
        
        // Insert a fragment into the document in the correct place
        rthing.insertFragment = function(frag) {
            var elems = $(".content").children(".fragment");
            
            // If there are no elements added, then just insert it
            if(!elems) {
                $(".content").prepend(frag.html);
                return;
            }
            
            // Loop through each element until we have one which is too "large", and then insert it before
            var orderMode = -1;
            switch(frag.type) {
                case "lesson-start":
                    // Always at the top
                    $(".content").prepend(frag.html);
                    break;
                
                case "lesson-end":
                    // Always at the end
                    $(".content").append(frag.html);
                    break;
                
                case "section-end":
                    // Before any element that has a higher order than it, or lesson-end
                    orderMode = 0;
                case "task":
                    // Before element with higher order, lesson end with same order, or lesson-end
                case "section-start":
                    // Before any element that has a higher or equal order than it, or lesson-end
                    var added = false;
                    elems.each(function(i, e) {
                        if(($(e).data("order") !== undefined && compareOrder($(e).data("order"), frag.order)>orderMode)
                        || $(e).data("type") == "lesson-end"
                        || ($(e).data("type") == "section-end" && firstEqual($(e).data("order"), frag.order))
                        ) {
                            $(e).before(frag.html);
                            added = true;
                            return false;
                        }
                    });
                    
                    // Otherwise just add it to the end
                    if(!added) $(".content").append(frag.html);
                    break;
                
                default:
                    throw TypeError(frag.type + " is not a valid fragment type.");
            }
        }
    });
    
    return rthing;
})();
