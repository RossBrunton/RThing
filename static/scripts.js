"use strict";

window.rthing = (function() {
    var rthing = {};
    
    $(document).ready(function() {
        // Put up with IE10
        if(/*@cc_on!@*/false) {
            $("body").addClass("ie10");
        }
    });
    
    return rthing;
})();
