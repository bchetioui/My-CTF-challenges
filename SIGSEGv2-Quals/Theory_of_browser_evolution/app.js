const express = require('express');
const bodyParser = require('body-parser');
const sleep = require('sleep');
const request = require('request');
const puppeteer = require('puppeteer');

const app = express();

FLAG = 'sigsegv{pur1fy_mY_s0ul}'

// Loading assets statically
app.use(express.static(__dirname + '/public'))

// Enabling POST requests in retarded Express
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

app.get('/', function(req, res) {
    res.sendFile(__dirname + '/index.html');
});

app.get('/check', function(req, res) {
    res.sendFile(__dirname + '/check.html');
});

app.post('/check', async (req, res) => {
    
    try {

        // Captcha error checking:
        if (req.body['g-recaptcha-response'] === undefined ||
            req.body['g-recaptcha-response'] === '' ||
            req.body['g-recaptcha-response'] === null) {
            
            return res.end('Captcha error.\n', 'text/plain');
        }

        var secretKey = "<captcha-secret-key>";

        var processBody = async function(hasCaptchaSucceeded) {

            if (!hasCaptchaSucceeded) {
                return res.end('Captcha error.\n', 'text/plain');
            }

            var url = req.body.url;

            if (!url.startsWith('http://qual-challs.rtfm.re:8080/')) {
                return res.end('URL must start with "http://qual-challs.rtfm.re:8080/"\n', 'text/plain');
            }

            console.log(url);

            const browser = await puppeteer.connect({ browserWSEndpoint: 'ws://theoryofbe-browserless:3000' });
            const page = await browser.newPage();

            await page.goto('http://theoryofbe:8080')

            const cookies = [{ 'name': 'flag', 'value': FLAG }];
            await page.setCookie(...cookies);

            await page.goto('http://theoryofbe:8080' + url.slice(31));

            return res.end('Checked!\n', 'text/plain');
        };

        request.post({
            url: 'https://www.google.com/recaptcha/api/siteverify',
            form: { "secret": secretKey,
                                   "response": req.body['g-recaptcha-response'],
                                   "remoteip": req.connection.remoteAddress }
        }, function (error, response, body) {
            body = JSON.parse(body);
            processBody(body.success);
        });
    }
    catch (e) {
        console.log(e);
        return res.end('Verification broke! Try again!\n', 'text/plain');
    }
});

app.listen(8080);
