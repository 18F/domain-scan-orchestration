var pa11y = require('pa11y');

var test = pa11y();

let index = function index(event, context, callback) {
	test.run(event.url, function (error, results) {
    	console.log(results);
	});
   callback(null, "pa11y ran");
}


exports.myHandler = index;
