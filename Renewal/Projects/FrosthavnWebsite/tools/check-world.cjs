const {chromium}=require('../../FrosthavnPromo/node_modules/playwright');
const fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--use-angle=metal','--enable-webgl','--ignore-gpu-blocklist']});
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('request',r=>{if(/worldBundle|frosthavn-world-/.test(r.url()))requests.push(r.url());});
 const url=process.env.FROSTHAVN_URL||'http://127.0.0.1:4183/';
 await page.goto(url,{waitUntil:'domcontentloaded'});
 assert.equal(requests.length,0,'3D code must not download on the opening screen');
 await page.locator('#explore').scrollIntoViewIfNeeded();
 await page.getByRole('button',{name:'走进立体海湾 ↗',exact:true}).click();
 await page.waitForFunction(()=>['ready','error'].includes(document.querySelector('.sx-world')?.dataset.sceneStatus),null,{timeout:60000});
 assert.equal(await page.locator('.sx-world').getAttribute('data-scene-status'),'ready',errors.join('\n'));
 await page.waitForTimeout(1500);
 await page.locator('.sx-world-canvas canvas').screenshot({path:'/private/tmp/frosthavn-world-bay.png'});
 for(const label of ['雪跑道','彩屋小镇','工作渔港','高地营地','冰川']){
  await page.locator('.sx-world-views').getByRole('button',{name:label,exact:true}).click();await page.waitForTimeout(1500);
  await page.locator('.sx-world-canvas canvas').screenshot({path:`/private/tmp/frosthavn-world-${label}.png`});
 }
 await page.getByRole('button',{name:'回到海湾总览',exact:true}).click();await page.waitForTimeout(1500);
 await page.locator('.sx-world-seasons').getByRole('button',{name:'夏',exact:true}).click();await page.waitForTimeout(2000);
 await page.locator('.sx-world-canvas canvas').screenshot({path:'/private/tmp/frosthavn-world-summer.png'});
 await page.locator('.sx-world-seasons').getByRole('button',{name:'冬',exact:true}).click();await page.getByRole('button',{name:'夜色 · 极光',exact:true}).click();await page.waitForTimeout(2300);
 await page.locator('.sx-world-canvas canvas').screenshot({path:'/private/tmp/frosthavn-world-night.png'});
 const box=await page.locator('.sx-world-stage').boundingBox();assert(box);
 await page.mouse.move(box.x+box.width*.5,box.y+box.height*.5);const before=await page.evaluate(()=>scrollY);await page.mouse.wheel(0,380);await page.waitForTimeout(500);assert((await page.evaluate(()=>scrollY))>before+40,'ordinary wheel should scroll the page');
 await page.locator('#explore').scrollIntoViewIfNeeded();await page.getByRole('button',{name:'退出漫游',exact:true}).click();assert.equal(await page.locator('.sx-world canvas').count(),0);
 await page.getByRole('button',{name:'平面导览',exact:true}).click();assert(await page.locator('.sx-original-map').isVisible());
 await page.getByRole('button',{name:'立体海湾',exact:true}).click();await page.getByRole('button',{name:'走进立体海湾 ↗',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.sx-world')?.dataset.sceneStatus==='ready',null,{timeout:45000});
 const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
 await mobile.goto(url,{waitUntil:'domcontentloaded'});await mobile.locator('#explore').scrollIntoViewIfNeeded();await mobile.getByRole('button',{name:'走进立体海湾 ↗',exact:true}).click();await mobile.waitForFunction(()=>document.querySelector('.sx-world')?.dataset.sceneStatus==='ready',null,{timeout:45000});await mobile.waitForTimeout(800);await mobile.locator('.sx-world').screenshot({path:'/private/tmp/frosthavn-world-mobile.png'});
 assert((await mobile.evaluate(()=>document.documentElement.scrollWidth))<=391,'no mobile overflow');
 const fallback=await browser.newPage();await fallback.addInitScript(()=>{const get=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return type.startsWith('webgl')?null:get.call(this,type,...args);};});await fallback.goto(url,{waitUntil:'domcontentloaded'});await fallback.locator('#explore').scrollIntoViewIfNeeded();await fallback.getByRole('button',{name:'走进立体海湾 ↗',exact:true}).click();await fallback.waitForFunction(()=>document.querySelector('.sx-world')?.dataset.sceneStatus==='error',null,{timeout:20000});await fallback.getByRole('button',{name:'查看平面导览 ↗',exact:true}).click();assert(await fallback.locator('.sx-original-map').isVisible());
 console.log(JSON.stringify({url,lazyLoad:true,viewpoints:6,summer:true,night:true,pageScroll:true,reopen:true,mobile:390,webglFallback:true,errors,modelRequests:requests.length},null,2));
 await browser.close();if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
