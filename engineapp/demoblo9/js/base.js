// $Id: base.js 3948f2b7018e 2009/12/21 08:42:59 Oliver Lau <oliver@von-und-fuer-lau.de> $
// Copyright (c) 2009 Oliver Lau <ola@ct.de>

function resize_maincontent() {
   var maincontent = document.getElementById('maincontent');
   if (maincontent) {
      var w = window.innerWidth - maincontent.offsetLeft - 50;
      if (w < 300)
         w = 300;
      maincontent.style.width = w + 'px';
   }
}

var slideInterval = 10;  // ms
var slideDuration = 500; // ms
var slideTime;
var slideStart;
var slideTarget;
var slideDistance;
var sliderHeight = 60+2;
var slidePos = 0;
var slider = null;

function slideOffset(t, d, c) {
	return c / 2 * (1 - Math.cos(Math.PI * t / d));
}

function slide() {
	var el = document.getElementById('errors')? document.getElementById('errors') : document.getElementById('message');
	slideTime += slideInterval;
	if (slideTime < slideDuration) {
	    slidePos = slideStart + slideOffset(slideTime, slideDuration, slideDistance);
	}
	else {
		slidePos = slideTarget;
	    clearInterval(slider);
	    slider = null;
	}
	el.style.top = slidePos + "px";
}

function slide_in(el, height) {
	if (el) {
	    slideTime = 0;
	    slideStart = -height;
	    slideTarget = 0;
	    slideDistance = slideTarget - slideStart;
	    if (slider)
	    	clearInterval(slider);
	    slider = setInterval(slide, slideInterval);
	    el.style.top = slideStart + "px";
	    el.style.display = 'block';
	    hider = setTimeout(hide_sliding_div, 10000)
	}
}

function slide_out(el, height) {
	if (el) {
		slideTime = 0;
		slideStart = 0;
		slideTarget = -height;
		slideDistance = slideTarget - slideStart;
		if (slider)
			clearInterval(slider);
		slider = setInterval(slide, slideInterval);
	}
}

function hide_sliding_div() {
	if (hider) {
		clearTimeout(hider);
		hider = null;
	}
	var err = document.getElementById('errors');
	var msg = document.getElementById('message');
	if (err)
    	slide_out(err, sliderHeight);
	else if (msg)
    	slide_out(msg, sliderHeight);
}

function show_sliding_div() {
	var err = document.getElementById('errors');
	var msg = document.getElementById('message');
	if (err) 
		slide_in(err, sliderHeight);
	else if (msg) 
		slide_in(msg, sliderHeight);
}

function onload_handler() {
	show_sliding_div();
	resize_maincontent();
	window.onresize = function(event) { resize_maincontent() };
}
