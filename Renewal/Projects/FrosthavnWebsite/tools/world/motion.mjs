// Cinematic model-space paths. Pattern geometry is inspired by aviation references;
// elapsed film time and distances are intentionally compressed, not flight guidance.
export const AIRPORT={x:-190,z:-75,y:4.08,length:220,width:12};
const clamp=x=>Math.max(0,Math.min(1,x));
export const smooth=(a,b,x)=>{const q=clamp((x-a)/(b-a));return q*q*(3-2*q)};
function hermite(t,a,b,p0,p1,v0,v1){
 const d=b-a,q=clamp((t-a)/d),q2=q*q,q3=q2*q;
 return p0.map((p,i)=>(2*q3-3*q2+1)*p+(q3-2*q2+q)*d*v0[i]+(-2*q3+3*q2)*p1[i]+(q3-q2)*d*v1[i]);
}
function position(t){
 const y=AIRPORT.y+3.25;
 if(t<8)return hermite(t,0,8,[100,72,-65],[100,44,110],[0,-3.5,21.875],[0,-3.5,21.875]);
 if(t<11)return hermite(t,8,11,[100,44,110],[40,35,170],[0,-3.5,21.875],[-31,-3,0]);
 if(t<15)return hermite(t,11,15,[40,35,170],[-130,20,170],[-31,-3,0],[-38,-3,0]);
 if(t<18)return hermite(t,15,18,[-130,20,170],[-190,y+105*Math.tan(Math.PI/60),110],[-38,-3,0],[0,-.92,-18]);
 if(t<24)return hermite(t,18,24,[-190,y+105*Math.tan(Math.PI/60),110],[-190,y,5],[0,-.92,-18],[0,0,-18]);
 const q=t-24;return[-190,y+Math.sin(q*29)*Math.exp(-q*5)*.035,5-18*q+1.25*q*q];
}
export function flightState(t){
 const p=position(t),a=position(t-.005),b=position(t+.005),velocity=p.map((_,i)=>(b[i]-a[i])/.01);
 const bank=(smooth(7.7,8.5,t)*(1-smooth(10.4,11.3,t))+smooth(14.7,15.5,t)*(1-smooth(17.4,18.3,t)))*.23;
 return {position:p,velocity,heading:Math.atan2(velocity[0],-velocity[2]),bank,phase:t<8?'downwind':t<15?'base':t<24?'final':'rollout',speed:Math.hypot(velocity[0],velocity[2])};
}
export function yearState(t){
 const day=46+309*clamp(t/30),snow=clamp(1-smooth(74,158,day)+smooth(267,333,day));
 const autumn=smooth(216,254,day)*(1-smooth(287,327,day));
 const dec=23.44*Math.PI/180*Math.sin((day-81)*Math.PI*2/365),lat=69.2*Math.PI/180,hourAngle=2*Math.PI*smooth(8,20,t);
 const sy=Math.sin(lat)*Math.sin(dec)+Math.cos(lat)*Math.cos(dec)*Math.cos(hourAngle);
 const sx=-Math.cos(dec)*Math.sin(hourAngle),north=Math.cos(lat)*Math.sin(dec)-Math.sin(lat)*Math.cos(dec)*Math.cos(hourAngle);
 return {day,snow,autumn,night:1-smooth(-.045,.06,sy),sunDirection:[sx,sy,-north],sunElevationDegrees:Math.asin(sy)*180/Math.PI,iglooVisibility:smooth(.35,.88,snow)};
}
