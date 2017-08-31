'use strict';
const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const pa11y = require('pa11y');

var pa11y_api = pa11y();

app.use(bodyParser.urlencoded({
	extended: true
}));
app.use(bodyParser.json());

app.get('/', function (request, response) {
	var domain = request.body['domain'];
	pa11y_api.run(domain, function (error, results){
		//how to return json
		response.json({result: results});
	});
});

var port = process.env.PORT || 8000;

app.listen(port, function () {
	console.log("Express app started!")
});