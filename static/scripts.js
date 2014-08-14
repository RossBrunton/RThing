"use strict";

window.rthing = (function() {
    var rthing = {};
    
    // Loading animation
    var loadAnimation = [
        "&nbsp;&nbsp;&nbsp;",
        ".&nbsp;&nbsp;",
        "..&nbsp;",
        "&nbsp;..",
        "&nbsp;&nbsp;."
    ];
    var animationPointer = 0;
    setInterval(function() {
        $(".loading").html(loadAnimation[animationPointer]);
        animationPointer = (animationPointer + 1) % loadAnimation.length;
    }, 100);
    
    var getLineNumber = function(textarea) {
        // http://stackoverflow.com/questions/9185630/find-out-the-line-row-number-of-the-cursor-in-a-textarea
        return textarea.value.substr(0, textarea.selectionStart).split("\n").length;
    }
    
    // Escapes html, not 100% secure, also replaces \n with <br/>
    var escape = function(str, noLines) {
        str = str.replace(/\&/g, "&amp;");
        str = str.replace(/\>/g, "&gt;");
        str = str.replace(/\</g, "&lt;");
        if(!noLines) str = str.replace(/\n/g, "<br/>");
        
        return str;
    };
    
    // Compare order values
    // Positive if a > b, negative if a < b, 0 if a == b
    var compareOrder = function(a, b) {
        var a = (""+a).split("-");
        var b = (""+b).split("-");
        
        if(+a[0] > +b[0]) return 1;
        if(+a[0] < +b[0]) return -1;
        if(b.length < 2 && a.length == 2) return 0; // 0-0 = 0
        if(b.length == 2 && a.length < 2) return 0;
        if(+a[1] > +b[1]) return 1;
        if(+a[1] < +b[1]) return -1;
        return 0;
    };
    
    // Check if the first parts are equal; 0-1 = 0-0 = 0 != 1-0
    var firstEqual = function(a, b) {
        var a = (""+a).split("-");
        var b = (""+b).split("-");
        
        return a[0] == b[0];
    };
    
    // Insert a fragment into the document in the correct place
    var insertFragment = function(frag) {
        var elems = $(".content").children(".fragment");
        
        // If there are no elements added, then just insert it
        if(!elems) {
            $(".content").prepend(frag.html);
            return;
        }
        
        // Check to see if it already exists
        if(["lesson-end", "lesson-start"].indexOf(frag.type) !== -1) {
            if($(".fragment[data-type="+frag.type+"]").length) return;
        }else if(["section-end", "section-start"].indexOf(frag.type) !== -1) {
            if($(".fragment[data-type="+frag.type+"][data-order="+frag.order+"]").length) return;
        }else if(frag.type == "task") {
            if($(".fragment[data-type=task][data-id="+frag.id+"]").length) return;
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
            
            case "prompt-entry":
                // At the end of its form
                $(".fragment[data-type=task][data-id="+frag.id+"] form").append(frag.html);
                $(".fragment[data-type=task][data-id="+frag.id+"] textarea:not([disabled])")[0].focus();
                break;
            
            case "task-content":
                // Replace a specific ID
                $(".fragment[data-type=task][data-id="+frag.id+"]").find(frag.select).html(frag.html)
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
                    // If the element has an order and this order is greater than our one or it is lesson-end, insert
                    // this fragment before it only if it is not the start of the section this task (if it is a task) is
                    // in
                    if((($(e).data("order") !== undefined && compareOrder($(e).data("order"), frag.order)>orderMode)
                    || $(e).data("type") == "lesson-end"
                    ) && (
                        $(e).data("type") != "section-start" && compareOrder($(e).data("order"), frag.order) != 0
                    )) {
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
        
        update();
    };
    
    // Called when the document changes to update all listeners
    var update = function() {
        // Erase all curent listeners
        $(".prompt textarea").off();
        $(".prompt").off();
        $(".prompt-button").off();
        $(".l-click").off();
        
        // l-click click listener
        $(".l-click").on("click", function(e) {
            $(this).parent().nextAll("form").first().find("textarea:not([disabled])").val($(this).text());
        });
        
        // Listener for "enter" on textarea
        $(".prompt textarea").on("keypress", function(e) {
            if(e.which == 13 /* Enter */ && !e.shiftKey && !$(this).parents("form").data("multiline")) {
                $(this).parents("form").children("input[name=mode]").val("answered");
                $(this).parents("form").submit();
                return false;
            }
        });
        
        // And "up" on keypress
        $(".prompt textarea").on("keydown", function(e) {
            if(e.which == 38 /* Up */ && getLineNumber(this) == 1) {
                if($(this).data("rlPointer") === undefined) $(this).data("rlPointer", -1);
                
                // Increment it
                $(this).data("rlPointer", $(this).data("rlPointer") + 1);
                
                // When we have reached the first one, don't go any more back
                if($(this).data("rlPointer") >= $(this).parent().prevAll(".prompt-entry-container").length) {
                    $(this).data("rlPointer", $(this).data("rlPointer") - 1);
                }
                
                // No other entires
                if($(this).parent().prevAll(".prompt-entry-container").length == 0) {
                    return true;
                }
                
                $(this).val(
                    $(this).parent().prevAll(".prompt-entry-container").children("textarea")
                        [$(this).data("rlPointer")].value
                );
                return false;
            }else if(e.which == 40 /* Down */ && getLineNumber(this) == this.value.split("\n").length) {
                if($(this).data("rlPointer") === undefined) $(this).data("rlPointer", 0);
                
                // Increment it
                $(this).data("rlPointer", $(this).data("rlPointer") - 1);
                
                // If less than zero, clear the input and set it to zero
                if($(this).data("rlPointer") < 0) {
                    $(this).data("rlPointer", 0);
                    $(this).val("");
                    return true;
                }
                
                // No other entries
                if($(this).parent().prevAll(".prompt-entry-container").length == 0) {
                    return true;
                }
                
                $(this).val(
                    $(this).parent().prevAll(".prompt-entry-container").children("textarea")
                        [$(this).data("rlPointer")].value
                );
                return false;
            }else{
                $(this).data("rlPointer", -1);
            }
        });
        
        // Listener for textarea input
        $(".prompt textarea").on("input", function(e) {
            var elem = $(this);
            elem.css("height", "5px");
            elem.css("height", this.scrollHeight);
            elem.siblings(".prompt-indicator").css("height", this.scrollHeight);
            
            // Now do the left thing
            var lines = ~~(this.scrollHeight/elem.css("font-size").split("px")[0]);
            
            var sym = elem.siblings(".prompt-indicator").data("symbol");
            var rep = sym.length < 3 ? "." : "...";
            var str = sym + "&nbsp;";
            
            // One less because we have first line
            for(var i = 1; i < lines; i ++) {
                str += "<br/>"+rep+"&nbsp;";
            }
            
            elem.siblings(".prompt-indicator").html(str);
        });
        
        // Skip button
        $(".prompt-button.skip").click(function(e) {
            $(this).parents("form").children("input[name=mode]").val("skipped");
            $(this).parents("form").submit();
        });
        
        // Reveal button
        $(".prompt-button.reveal").click(function(e) {
            $(this).parents("form").children("input[name=mode]").val("revealed");
            $(this).parents("form").submit();
        });
        
        // Prompt form submit
        $(".prompt").on("submit", function(e) {
            var form = $(this);
            var formData = form.serialize();
            formData += "&csrfmiddlewaretoken="+$("#csrf").text();
            
            $.ajax(form.attr("action"), {"method":"POST", "data":formData, "dataType":"json",
                "success":function(data) {
                // Hide load animation
                form.children(".loading").remove();
                
                // Show output
                if(data.revealed) {
                    form.append("<div class='output revealed'>"+escape(data.output)+"</div>");
                }else if(data.isError) {
                    form.append("<div class='output error'>"+escape(data.output)+"</div>");
                }else{
                    form.append("<div class='output'>"+escape(data.output)+"</div>");
                }
                
                // And add frags
                for(var i = 0; i < data.frags.length; i ++) {
                    insertFragment(data.frags[i]);
                }
            }, "error":function(jqXHR, textStatus, errorThrown) {
                // Hide load animation
                form.children(".loading").remove();
                
                // Enable textarea again
                form.find(".prompt-entry-container:last textarea").attr("disabled", false);
                
                // And fire the window event handler
                window.onerror("Could not submit code");
            }});
            animationPointer = 0;
            form.append("<div class='loading'>&nbsp;</div>");
            
            // Lock the output
            $(this).find("textarea").attr("disabled", "disabled");
            
            return false;
        });
        
        // Clicking the promts will focus them
        $(".prompt").on("click", function(e) {
            if($(this).find("textarea:not([disabled])").length)
                $(this).find("textarea:not([disabled])")[0].focus();
        });
    };
    
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
        
        // Error handling
        window.onerror = function(msg) {
            $("#error-body").html("Sorry, an error has occured: " + msg);
            $("#error").slideDown();
        };
        $("#error-close").on("click", function(e) {
            $("#error").slideUp();
        });
        
        // Fix Firefox being dumb
        $("textarea:last-child").attr("disabled", false);
        
        // First update
        update();
    });
    
    return rthing;
})();
