
/** The passenger stays inside the cabin until the aircraft is parked. */
export default function WindowFlight(){
 return <>
  <div className="xp-window-flight" aria-hidden="true">
   <svg className="xp-window-aerial" viewBox="0 0 800 500" preserveAspectRatio="xMidYMid slice"><g className="xp-aerial-land"><image href="/assets/experience/original-bay.webp" width="2030" height="826"/></g></svg>
   <svg className="sx-flight-clouds" viewBox="0 0 800 500" preserveAspectRatio="xMidYMid slice"><defs><filter id="sx-cloud-soft"><feGaussianBlur stdDeviation="14"/></filter></defs><g filter="url(#sx-cloud-soft)" fill="#dfe8e7"><path d="M-200 40Q-75-10 85 50T350 100L280 142Q98 112-50 154Z"/><path d="M340 378Q484 320 640 386T980 398L1020 464Q784 433 648 459T340 435Z"/></g></svg>
   <svg className="xp-window-ground" viewBox="0 0 1000 600" preserveAspectRatio="xMidYMid slice" shapeRendering="crispEdges">
    <defs><linearGradient id="xp-arrival-sky" x2="0" y2="1"><stop stopColor="#20394a"/><stop offset="1" stopColor="#8b9ba4"/></linearGradient><linearGradient id="xp-arrival-snow" x2="0" y2="1"><stop stopColor="#b5c5cd"/><stop offset="1" stopColor="#8fa6b4"/></linearGradient></defs>
    <path fill="url(#xp-arrival-sky)" d="M0 0H1000V600H0z"/>
    <g className="xp-ground-hills"><path fill="#506c7b" d="M-300 280V233l120-18 90 12 105-31 92 14 110-41 81 9 115 32 99-10 88 24 100-13 122 27 108-11 100 24 220-8V340z"/><path fill="#8098a7" d="m-300 235 120-18 90 12 105-31 92 14 110-41 81 9 115 32-115-16-82-7-78 40-100-12-118 24-83-3z"/><path fill="#344f60" d="M-300 280v-17l143 5 134-28 111 15 122-7 154 25 112-19 139 16 140-17 160 29 230-11 190 20v89z"/></g>
    <path fill="#9eb3bf" d="M0 282 140 276 260 288 411 280 570 292 729 283 1000 294V600H0z"/>
    <path fill="url(#xp-arrival-snow)" d="M0 326 1000 310V600H0z"/>
    <path fill="#90a8b7" d="M0 415 1000 395V565L0 600z"/>
    <path fill="#d1d9d7" d="M0 409 1000 390v4L0 414zm0 171 1000-42v5L0 588z"/>
    <g className="xp-ground-travel">
     {Array.from({length:30},(_,i)=><g key={i} transform={'translate('+(i*150-2400)+' 0)'}><path d="m0 473 73-2v6l-73 2z" fill="#e8e6d5"/><path d="m24 332 27 1v2l-27-1zm83 36 18 1v2l-18-1zm-8 192 39-1v2l-39 1" fill="#728e9f"/><path d="M93 389v-11h3v11z" fill="#4b6473"/><path d="M91 377h7v4h-7z" fill="#d6bb83"/></g>)}
    </g>
    <g className="xp-ground-village">
     {[{x:90,c:'#9e614e'},{x:217,c:'#a89a67'},{x:359,c:'#607f87'},{x:645,c:'#96765a'},{x:789,c:'#8e5a4c'}].map(({x,c},i)=><g key={x} transform={'translate('+x+' '+(285+i%2*7)+')'}><path fill="#59717d" d="m-4 22 58-3 15 7-57 4z"/><path fill={c} d="M0 0h43v23H0z"/><path fill="#485b65" d="m43 0 9-5v24l-9 4z"/><path fill="#d1d8d5" d="m-6 0 26-16L49 0 58-6 31-22 20-16z"/><path fill="#f0cb8c" d="M6 5h7v8H6zm22 0h7v8h-7z"/><path fill="#3a5563" d="M18 11h7v12h-7z"/></g>)}
    </g>
   </svg>
   <svg className="xp-window-wing" viewBox="0 0 1000 600" preserveAspectRatio="xMidYMid slice" shapeRendering="crispEdges"><path d="m448 416 121-20 431 117v87H892z" fill="#2c46598c"/><path d="m419 396 126-20 455 108v87L583 431z" fill="#bcc8c9"/><path d="m419 396 126-20 455 108v21L583 418z" fill="#e0e0d3"/><path d="m419 396 30-48 15 1 22 36z" fill="#a86650"/><path d="m464 349 22 36-10 2-19-29z" fill="#d4d7cc"/><path d="m583 418 417 87v9l-417-87z" fill="#758e9d"/><path d="m702 447-4 23m130 5-5 30m-240-87-3 12" stroke="#7a929f" strokeWidth="2"/><path d="m730 488 270 65v18l-273-69z" fill="#8fa3ad"/></svg>
  </div>

 </>;
}
