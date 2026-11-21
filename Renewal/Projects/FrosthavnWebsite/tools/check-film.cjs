const {chromium}=require('../../FrosthavnPromo/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--autoplay-policy=no-user-gesture-required']});
 const results=[];
 for(const viewport of [{width:1440,height:900},{width:390,height:844}]){
  const page=await browser.newPage({viewport,reducedMotion:'reduce'}),requests=[]; page.on('request',r=>{if(/\/assets\/film\/.*\.(m3u8|m4s|mp4)/.test(r.url()))requests.push(r.url());});
  await page.goto(process.env.FROSTHAVN_URL||'http://127.0.0.1:4182/',{waitUntil:'domcontentloaded'});await page.waitForTimeout(500);assert.equal(await page.locator('dialog[open]').count(),0,'homepage must not open a dialog');assert.equal(await page.locator('#film video').count(),0,'homepage must not mount a film');await page.locator('#film').scrollIntoViewIfNeeded();await page.waitForTimeout(500);
  assert.equal(requests.length,0,'no film media before play');
  await page.locator('.sx-film-poster').screenshot({path:`/private/tmp/frosthavn-poster-${viewport.width}.png`});
  await page.locator('.sx-film-poster').click();await page.locator('#film video').waitFor();
  await page.waitForFunction(()=>{const v=document.querySelector('#film video');return v&&v.currentTime>0.5&&v.readyState>=2;},null,{timeout:30000});
  const before=await page.locator('video').evaluate(v=>({time:v.currentTime,duration:v.duration,width:v.videoWidth,paused:v.paused}));
  assert(Math.abs(before.duration-199.7)<1);assert(before.width===1920);assert.equal(before.paused,false);
  await page.waitForTimeout(500);let music=await page.locator('.fh-site').getAttribute('data-music-state');assert.notEqual(music,'playing');
  await page.screenshot({path:`/private/tmp/frosthavn-player-${viewport.width}.png`});
  await page.locator('.sx-film-player-bar button').click();await page.waitForFunction(()=>{let v=document.querySelector('video');return v&&v.videoWidth===1280&&v.currentTime>0.5&&!v.paused;},null,{timeout:30000});
  const after=await page.locator('video').evaluate(v=>({time:v.currentTime,width:v.videoWidth}));assert(after.time>=before.time-1);
  await page.locator('.sx-film-collapse').click();assert.equal(await page.locator('dialog[open]').count(),0);assert.equal(await page.locator('#film video').count(),0);
  const dimensions=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth}));assert(dimensions.scroll<=dimensions.client+1);
  results.push({viewport,before,after,music,dimensions,requests:requests.length});await page.goto((process.env.FROSTHAVN_URL||'http://127.0.0.1:4182/')+'#watch',{waitUntil:'domcontentloaded'});await page.waitForTimeout(500);assert.equal(await page.locator('dialog[open]').count(),0,'legacy watch link must not open a popup');assert.equal(await page.locator('#film video').count(),0);await page.close();
 }
 await browser.close();console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
