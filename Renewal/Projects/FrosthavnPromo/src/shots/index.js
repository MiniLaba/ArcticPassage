// Map every plan.json shot id to a view and a builder. Builders receive the master timeline.
import {Invitation,Landing,Town,Fishing,Harbour,Neighbours,Beyond,Seasons,Night,Home,buildInvitation,buildLanding,buildTown,buildFishing,buildHarbour,buildNeighbours,buildBeyond,buildSeasons,buildNight,buildHome} from './frosthavn.jsx';
export const SHOT_VIEWS={invitation:Invitation,landing:Landing,town:Town,fishing:Fishing,harbour:Harbour,neighbours:Neighbours,beyond:Beyond,seasons:Seasons,night:Night,home:Home};
export const SHOT_BUILDERS={invitation:buildInvitation,landing:buildLanding,town:buildTown,fishing:buildFishing,harbour:buildHarbour,neighbours:buildNeighbours,beyond:buildBeyond,seasons:buildSeasons,night:buildNight,home:buildHome};
