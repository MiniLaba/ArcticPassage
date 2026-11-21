import { createFileRoute } from '@tanstack/react-router';
import Atlas from '../components/atlas/Atlas';
const title='霜灯港 Frosthavn · 焕新版地图集';
const summary='展开霜灯港三公里海湾的地表与游线地图，探索灯市、镇西冰屋、北界冰川和可互动的三维沙盘。';
export const Route=createFileRoute('/')({
 head:()=>({meta:[{title},{name:'description',content:summary},{property:'og:title',content:title},{property:'og:description',content:summary},{property:'og:type',content:'website'},{property:'og:image',content:'https://frosthavn-siming.lovable.app/atlas/coast-chart.webp'},{name:'twitter:card',content:'summary_large_image'}],links:[{rel:'preload',as:'image',href:'/atlas/coast-chart.webp'}]}),
 component:Atlas,
});
