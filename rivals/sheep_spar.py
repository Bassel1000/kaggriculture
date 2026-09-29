"""sheep-sparring bot (TEST ONLY): v68a + d4-d6 cow->sheep blob swap (~10S/5C). NEVER SUBMIT.

Kaggriculture v3 - scripted season route (8 cow / 4 sheep premium program).

The route is a 720-step action schedule reconstructed from public competition
replays of a top-ranked agent (via boatlee's public notebook). Execution adds
live-state repairs so the open-loop plan survives drift on unseen seeds:
  1. hand alignment - pad/truncate per-unit ops to the live hired-hand count
  2. weed recovery  - DIG a weed blocking a scheduled PLANT/BUILD, then replay
     that unit's schedule shifted by one turn
  3. premium market lead - move part of next turn's MELON/MILK/STRAWBERRY/WOOL
     sale one turn earlier when the town demands nothing of it today; the
     moved quantity is deducted from tomorrow's order (two-turn total constant)
"""
import base64
import copy
import json
import zlib

_ROUTE_B85 = "c-rk<%Whm*a{QGB*RxPPNYUQ0r5d*|98sXCDU1c8(SXM=V2l@S?+pLD#U@#Gt8QdQMCK`~yGOecN!_~Vl_xVYGV=5Pp8fkzKmYx2KcD^ccc0HbTz&j_cK?U(&i>=4|N6K8e)!SDKmPvH&;R+i|9SY==d<rW{q@HWw>NJ;y}3L4@~iC+o2!Qp>o0%z`Rs>xx0|!0PY?g$<7V^r;jjO^xxRV-<-_aQZ=RoXzWdG9`*(l7x_<cG#~(JE55IiJ{r~;pyTkW=_vTNZJ{<nh^zA>NZ8sn99$)1B&F$R}XZME#N}f0!n(@SBie_K-{ik==Z-4wU>35$Vr)&B>Pfs^q{rc+7W<M84kNfi5_jmh6FrNFzhc!B$gsZ#F?c+m^A55P1<|-ZP(}T%FcK>0_2-9__4>ezq{XWvhjFw^dLXVs5@oB$2x3CImpij@OEXT*2Pu`-YtAG~w=^J{hP#!cq7Ur6wWk74HjdVBT!2q?VJdYt-OJ#e(H>oe-@9KPRu7nAkU&IFkecU(At4zGN&cn-kaW725@wXr!0ecI{*UX2uV7Ih>8$jE*-wa2e*u!qFuQzY*e*EL+_U_&FyMKLL!9i~d?QZ#1(FUHs(yw+NJFlAi6O+UHd@fbX#e668aqzy_J!Ah#vN3#0(W4tz5qg|t$<UPq9|lG=>P4j~g?9jW*xTEi5A<P=-^d^K`03cre%xID5<N}k;?YWCBfC<J>?-lwcgGpOPH?#_=U@9cH~c70z8rmJC9;csL35s0vw8k_cYC${esg>KSA3(vQSX*`W-`$9s$az?LfvKND9nes{!8pxn7+Foc^mGC3rOU*sDCMQe`LScrXRs2?VM_O!*;H0a<k4q4)Rt`Jk53ZW2oP^vwss~a%dQjf6<s_I1{2nMCW-Dy4o-k3#ca#tjE?9t5`*Ih!bPas_Mp+p{BZHS#w&o<?c9K1@B4s<pMKnyAgvg;I=!u-nmI&bgTQ{ihJSudb0N+ov*Kmg}ATkfFbUUYd9F?TM^$>qi0gPNF6+c_;I3tar}^;uQm<eLT5uc$GS@~Xpc@jin()9xvB93wS7R)`pHLWGMUHod_{_n%N+^wa>>n*TpPgN<{k)MaB+aS%V5ry<1##7g)b18hgj0fI}EGejK}i=?#7%UA^I9~*2JO`H*&`V|HTP0knyPm`<^GUxqZ=-yK}G~VkfX)elBOp;4kOm>h>>Vvb9I~;OT_yz9hq5_eoP};-BB5!$aUp@chlw3#kEsOt0-2moNA&9Y_qm>A}93ymqjZb;?bB@rd&}{5Z~@DCf3VP*6C8EM}`yVUS;jEs^#-Hu(L)5`n<y{~8=D_j&W1_B{12p1rHXdl~v%=b;m#ehRUXRX;O>{1(E^tmny$tPc6%ScixG@RYDjZ=g16(;O-x?VWxVPdGL!=d_PrQU|TKkOx-+%txS0qqmxV<_h^U$={4lbnU&f`K{zQD}4F)m&*QAgnppEmEv6F*zF&&cX%;KH3YB1&qE_}uUYtYvxi6@%X}hvNc)X7Dz%nO9NH<-Fz4=v&zC_C-X0U1ycGPQN$ctWbJ5S>n%K0hbr%qeKIQ9n<RIGaXyuK92@5yP$)*O8_vTxA`7*OI1X%X4$8sXH#Un?fScdNZ*CKN@zk8U+DEVv?=Zk_;)Jq)YqfXo*<QU=~mQ!Vs|G7<^(w=`BIb1Zz9YJWDyRpf~%}1wVCD=?mOm%y6^I#t@k|EB}N#UN{J+{IWdVV)>*=E^p&R|c>;DwjJfeFSStpa1Z{dwB|I)t+2MBmY>E|v+1hvL3G>8f%0XPe+MdC`LrNpBm0$McWmwU*VI=IH*}8|XX$ke$tg7ghHFa;Bh*orQOTKQ*-*ej@sLqR*8#MH8!V^RBPnzdbAYd-NpdD=b-NWJ2Olt@TxDp=SP_*_F_$<Ah6TgGAmhntUi^F-LRT3F%5XxIMB6OR2#3*lx6QX)8s%NC<>(f;Tr?HCl|7C~$yx;8AVB{Q&+~oqCMS40N5)OO2`6oIGW3%CQeUGd!b8&;yIk4Bg}VwhSF~`taz(!!MO%5^8Md+l8egDA+30aw0Q_HXFv-UwjLO^C9g8bwf`4|LFVh>uDMT@{Wwc-YmQ>?gO$vp(#@6$n_d+975(y5|^Km+g}2vxQP&Uc~cAn7T5xSuj*ao$73_kN0Aca$*T`A)#%G$9uRVg!4-2Fiyb(C;mfz|GfSiO?go;%Q_M0vI5>FK>tY$<KH+N}FN@&K1yxw46cY&$lzh4*fI!X=td3U}FZ0$`y^;pJqpAuJ``3Gp5)@7sD6#8AGr2g=>oBB|7*$IOh@2bY%ehC`aY_%-?Ft<{#C2%IIS&4dy$t7%rL<9M99ZN5Z@IeE;lox_6D;uicsj;LTXY?zc7Cl}1qD-m$UACG2in2=U2uT1!w9xfcL=}QS@7tO!?a;v=rAkW6at8YH&dx&*>OUcI1F-$b6+mH1pzD$n3(C2{C0Fo23Zv3zm?^$pbH4ULS_9GUIJcwYC@r|m;p(I&?}w1Rpc0&1h8k{CfcKufHF-h*%b&pEf{S)lmVV`11s!ACi_}T@`j|nA@ZeYpQ5C~j6pay&2bbzhTk2(WN#WEl`Kdi7zNv{N#Wn`u`F9>S{m8q=}KdgeD~^pNGa|*0qUZ^j(%=MSLc~B8w1r*Ah@@$Nyvp0eA@TJKu?IVqMtW%-RN9HUm1F9Ec&XOeT&w%pHJ(*^(hD`pYCvi;8kr`sA!%w-VX<^JWeKg6usQLwgRC2e|!7xUjp~LvXg_a!xN;q8p8^DnC6~{FD^K*Q?~`Eh!mMXR1*SYd$WF5Hbzm!7Yx~KG>8&=ox&#}d~>G>iMjK-E0U*!_Pt&lP4X}~<<Jgh)Hi^ZnR)Ydy#PkF4=l1u7HmLrjz#vki(01|hqoV>6KMs9D#7fD8M+daYCIY};0Mn6%|RBzTXMAXSzHD=%&X!X&E{|67vE7?5GlG`#BPT<gd|v6yF@h-Z5lCZR|wtJbQqK5i=tF5O{Udt<-sJRY)O?}X5r$cT)MUjTbVTp{Dc<C2AfftjLK4D&Ff&!LL&x=g>=rxR#=4JlIRvlKE5vX04g<FiHqEuBgw7VpA6yfJH_X4ap*{dT!2_=*-BY({|8sBd*n^%Ld#b2*|=S(t`+b-;RNo7mWsZ|Wvv8%K|?So_fEYgNu49=j>U1SS7MSPVu<)8l?39OZ<zV$6Bww8aBxL9zj!GoyLLlu$aaJV8Vq)WDV{7XdQo<cNYXDmQIBPBQ`b8&92RPfz$ppJ+i0$1dgKN-IYIZ9QHwxUGCPe0zlX=^DB=W?oXYvg7lsT++H|A_p52|t=sl<8V04;HM%y(){#@Yupp%6U5VU`CUH+l9NMa8)Wt?Npc;5FfP7Esk?+|Fj<^Hje)GSBM^C0DYdhVmZ;2u<;r5*ji$OK6j$X5`E;iF`-;Fuz>{>Z>6s!Vj@M)~!`LX!eES<*?Y&6bR%#+P2r@`rixP5uc%-vjtvUjywc0($2uAs^qkIo`E@7PvDS7@tnZ`Le3FH+Q>7V3qI0%CC!x6&7enph9L-^9w{+4U6*QdI2lV3lN}2wgWA1HJ`K*UO1$a+R7BE-gQOpwk3Sa^OlApRej8Gp+;$!@#x9$J~Lv7JO|#oK_>v(9k<TTi{05qu$N9fWTgt`x%cz5=GxiXJ?GIoJATATjv9@DYm3p+sBt=pP`cM-E-@;e-<yZR)!?CthDpIeB?STuEy63Xd+jGjMme6~Pi?n#shl%3B0TBSSAstb_8-Ng>$fwnvq0~Ohex#^NLUW1XWlNOv!IKXss|Y<wM5jsz^U+(4PrW#I+VGua&WkkhEQ=HE$;%~0uFUb0ufSyesU~m(aVl701(l72qQfZfE@DPCgl{DS%O!B3jqmvNOi><8Eo8?MoB2`0bXfxyDB$5RDUp=N$b7ZOq-X#T)r!FW!ZW!c$B1PoISNf&XH|(n;Zx%e@&>cwg`>J5HRe_N*h(}d0`!@pyT>0Q4F1OESFFy;J+5=<w<&^z$8KyMOr1fyUE}xQu*mfRG<@Tk=E<yD7CI6%&!BIf$TYQQHUOl5q)bU!4ieW^-&0?!D(Jlr_114NA6V_D94Dvk(^jY4UIzD0nKzLzG86XNbDZe#Y$0bt+4>#kgV8M;JI#XDHRLGI;@4`&J8b0!m*FnleEiUr8tHT2@Ijo8AP3EOT@v<K>Vn3p~J`z?TD5%BMG=kQ6kTZXv#cB`b9ceY;KQm{H%3dGdl2&zFa72iuaT34~ZJ77Nj1$wFJd@omo+SMs13qyTXKXLps-OH<{v+uAno7oyR-mWfb$ZSX(Ef5c|<v;yn%%0kuCtYlkBCeChOB!X2;c-SwX^t&2Ai2xq;#N-{=K>LlSsn`o8L+MsvNt60I-X^w35Yc2tO8G0BaYDoPgM5Uk8Fs^chB~FvnGgW;`RCCsgV2arFk<c`#geuM-)<tyMgbSms;gBYTBWO!BVM}Uoprbm%DJ_CI1b-V`LQF~p9s1YkhLG0IrEh0s#haF52wR9T?AVSns>sSTApLF7UuFU1X^1`Kyb-mJ4uPyj)j0**VN;sk0?me@>oP;Ye0iN5LulpX{W#P(x_*vn^2zUx^6vF~zLR|^O!QU-p-&_TEa)HRs?u2%Sxa0ycV=Kz3uidNa+-5WMNlwJBUKAK{@DotBY)cSS9WB@US<gdyc4&$L>Hr}ZLDS=VUe%0BL=`7lH%3HSAshR3t6wlhBZRfo6zV5K~wmbOT8lwn<>!f6i(tro!uh)6)s$J0{b?C=HfF#^ja=)-Cy^lATa=<i+zdlvb27xCW)Jr@8S+_`z0sNVem*E$WU;^%O{yhXZ_q$c%)qZ;e-y#DQ3|mgQ(1`ex51iO_*2-rB0?98N0LEFWL<$JOoD>|CD-F^>K0$42C?!ot0e7&?E)%ld#jW*kvOl-q`Up>$@yoAWOPQ&BbHo-KA8wOgXA0o}uq=Evreph28-TTCjkm$nytyDUZmlYxg=K{4<D}q=${f)uEvnDR{>kvFY8<;b;m(GSWXq23`raBd4r-H>8DEkpdf*Wu-Suyz?#0ka->!!Lz`RGIi)EsD%xRK}^$9e58RioK?2^@Fi9LUT8@!e8F})$ry2fuP<{MDVxcYq0VW``%g&B9R>PGx+~LnLLeGiG2B5JUh63%ZThR7R?*`AS6btB5~X;duqy<<4B%}HvUaq+S047b%67>pZWCifGlQU_k!7Ndrz($2;PSL|L-(7Of)NB>h(5(G09CqSqdW{%-IQcY!dW1<#>4~$mT`bB&9hb#+F-Q>C}_85ub%_$F5q&|9?IFe8FVLwy9>)0<^^vK`-)+TNw_t($n8KD4xlc19L0ulw3_mMOZ>IhT?*G!TL)k=3!9ZDV4ehtc$)F0>c3?tlh7OwsSv>>hypMKVThd-MzJ5OaVY(mcPuG*7kOE&bdf2D_(rQ9g4=8N!-01<1d)iQ*kn5$S&I@3UqETLpb;Od_@!Hl92d0+m~$s#ywCR^YyE`9i&Lau@`;|do#;~FJIQXiNhTmdpkq{;oU{cVGX3GOxO^d{A6ANbKieo;I~NI|A)dB}*GKJVpkdmz9%gw}pRX%j=<%tjb+f|fh8k2j<Rh!xT4kxKjwAA-=ay$@q@eMbL?A&ivmX|UDRH_fqWvH+k>SYL1Cf};Xw^{3L0+*+T_A|M)NjszP(i8yKU-<I<;sCKgUEXhNbZ^s(jUfWNagy$&EMntiAe1WDpr*^Of|GmLdBpxJb29cC_W(Kg#`XD%LTfXO?B2EDYvM_98RWa6dBNpG=e|Y)zsYjA)$?5j29CPUDD3=bjZ0t6x@hV-O-S1K!e#}i+QOu*WyTXTUhWbWWp}wFl>lYujtxl3#YO4X8$eh6i^M`aj_eP96gXoAFLL->rpo{J+lAdBnZ+pP9=F$yJzuh#L=PAG)LHa%+Jt_ka-wcHw9%H!ho{QXNEgU?@K5&9|wq7X`>Cio$*H8n5?N<@(kg^v`aX1)D!WwLeF;RNISGVPx6jp4&~lK{H2Ms8O_cn(P1H}kfJuruu}lhC5sYO8x4VkE=_Dg8P^YXvj#)as;h@7_;GzW^twz<op6_`0BCQHQ_yCTyUqS=&`SJH1jdLoT}}VJBsLb59%6=Hd@~dYd;~SCw1bpeKMLuviYP#t@>eUtr0AMXNLEFm<jM_ya3@iOa@xqT3grr|O*=tD6ruzVm!e}uxTB$jmWbPV>PAeR|HV#2G;@)3cM(`}qoPC5SUw=EW1Y@Hjxe#Mj)x5I2%*U869QtqmI>w%DrRc@DddyFh2VS@hJ}iuzQ{-@u#Z@?Hzsix9lPk~<uWj2AZQ3LQ*$}9tHuggXl8=ApTt9hfwPeiTsBxb($OcXm%50d3%+raCX}n`z!efna_BZ;%XC|Z%2Qe+gCWvTMEXOe>#L$HH0gxhpZ%M|G3xz5q;Xz|5luqtV>wIs?mCf3WE@vnFH1?pfsBDguH|GVQhUcG22yWH<~3U>t3=I#6A&*%R$`O8v{F&#Tq2HUKgt;vw7{q(gZzF6_u26?`;|)JuU4g!;KgsOBzO?&mtyvLFAD?jT82(Z2-7OF7%YDa4`dXW0@kU^l_ma6)bH}V2Lxhs9Mn!3>iPw}K>ehe(a%9<I?HO36^&AzOw-LrLwJFUD!s2YzLQdZW|d`xNGN*pdg*U#861#v>vTjjXpMsUlStw*Rr2whvES=mH-<~P2Pc8ZBN^MOTWIG5`-rU-)v`h8h>5u!l=$$VOg-&*W?Lwy)3yUmTcS-iP@t0J`ADzUobcRf--($csFagQlLmkw=}$>iHLZg0b&sMQ?J8E6yE`UuablXAwm{sl<pt-+z6GjXZf967y5!Q^AbCx=@ty8d71Uo5GFjgH+&HT$z_?LE24zF%&f&`mwmmnEF$L7rXeHxpvS9O82~rC#we&-zIS#H4W26<XGfEof;w}u;J~-^e^L6CXs)RJ@VDqI~7HAuEDjpF)%<5jr)qF0JLkRa1fjftY5~`M!`}G=vfjVfcs~4=$BxO&2)r6{k7nH(O`cLB<_Ou9Br}^bl!YRdaL<gqS``MG`l9mAB(n!%Xo2|w*Ppm@4)Fm85u{ekr<{rDC@fMFb{WuVmfUu+2)if?BJ^D>N+JdmtfmJ;>lxUimpj9)%%bM*rH9gWJJPK1TVPnhkdfPDtm+}FWYS`rM>Neu7A^vI$$A(B|O&7Fte(J2?Xu@*hT;2pjg+to}M`{QZKsQ}ZDPlSAF&=})FECpuXt?I7w?_Ayv}6(XLQK0=#N)CQ5xVThyz_zEWIB3AjA{>bHL$fdfn7cy+g3iup+f3q$t?L7yz>!C-R!z4xGt9H1aB!ZNS?s-=L|litcsLttmTdaWXI|JX@EVP_j!|Y$mBQ~QuCn7fYq7=i*}jU9!ZT_q$Vqx<;e+{EEj@#yIR?7esen5=tYx4Dcox*N<m-|!I`X>r#LN<b1vcX1q@2kHHk+JMmi~}dWcWn?}{NQ!h#xSvW79982(&p;t49U=~XSC2J|HNSV7pJC2Sal3=qns)I({QZQoYrPinyt5hX$YuW(65<&G|{B8bvwUv<i^#1T${0R~YtO@)kl>=2>EDuy4K>&aT*G{HxQD;Dntj7M(tN=%w07)BT4VR^BFG=sBL(Zb#dN~s><K8opO5kU;wi?T{4Qx-e4c0vuK$UyWuKA4~prC1Tjkw#qnMzR}j7cWl~WzjVd^dOVur`5E99x~YP)k+TvnMWqv&ZGdUtjuM|%0%0a>B{WjmZO+B?q(_+rCw7ZM$-&ne5x40xX-eY-%%G6isq^MI0j}uOyINlLrQm)Ic8~3HlB;JGBYIF7$D?WFD!D1fsAmV7xGE_7e&UGy<R5-mL`6e(G>a-q&`72LDWQp6{>AjQF{oG#vxlyGht9B?`9Gj49Ij0xEN9HV577mvbe^OSM&6j{Y4IPLcB^o#k1gw?`MhUPK`bATPy^Bsdg(Qjh{e2-V|}<S#6L~>eVbK2x)oy;_G!y5ybbPLr~J~@Vh)Cca-fkh73jSPOj|o0%C8xw%b~wN_UZR4jo>>lAal>@el(%2hVF*3dx72NSL*bdRbcnSEeC?Vls@18ZJXfK<lx}12m*{)NctC(})wg?BgI%?KjJ6N=f=9ZSjO`^Uegy*`#+^LRy6Eif0~{eoT*=fO#JFO6|I1007X@nMgc=jgGVga`eiGwixt{jCCLap|q3Uh<$gIF6TPFf2dNnED2aG?+3|H6S;l8Lz~v<Kn$}*buOsf#^x!wL}E}gmrP^;FpKS(qfqEe$fy=pUtOzL*HQ_Z7<*$<3kqxv*+{ICA6+CkUnB@K5}8@%;O1O&lDOGi-@IqFtb@a12(u7JkRA$6Eo6nyz3J{U=g5JKavQ1293E`fb*Au2xzD;R;tNEyku}{bMXLR&Npbt^*VSAKBt#IT8RqJUjO=z!<cFu_xI0hb=495uZ6LIamBEmFvqbzB7S`^aqRPOoMx7tBclO2r8Xz=xPU~BF(|l7f?JJlrhCtaUDY$56u6fC00iGA<qg?wsM2=JfO=<WqG8=2+Nr*3tyxT&<o0gh)z4n-}J&K&=I;*8YlXWPVs*G1tK8+$bj`WyWQ9URL!W2Y<qzCUP%GlXM^b#@G-KeN>ZtwyWUOWN_9Q0mKCHwXcfTR>GUu`LlNer2E8Yp>{m5LUcyvS0c<GHLb{3pF$gw!AYsdgSLN-DhZEdDA9V+aN7m%TTTm<k;Y?m$FGob*gmYj+tGN4TjW|1vvMTp>Wxd#!>9#fGE7P|0BriDhJ;qB*KkpK`oS=nctT7Sh+sKowQ9O&wOtuyh*Bo{Wi-2{#8Q6=qm&q>A@Km)qxrsNcrNB_ihC()7IlXc^866%N*W1@{Va*AkhN&{_j$2J|971X{x?3WKD)*7gSMc0?si*`lK^Nho1ZCS51n;8<S0(f;b2FsUg_n*MU_plpgRr)5*Pp((c4dKD0MlOmp%)CbsZY#>zUPmXNQu85zK6nnE{c*Tj=wHT>5B={Y2NWQWJs#J%WJM%7>+h7QK1;Oo_^qw{;O9Tj{V^)|KQf;uPiFpKQkD^>BOaTAwt-~}(QC+-JgqLeC#~bCey)2Z#GuqoSRXbzHy`Z9KW;cZfV~l;)k_?5HGHc1h6xCdyHb1L5N*f;8P;^o)u@Q+3UD;5f_dL}JCP$*)_mJmScphe(7OV4HZ4~Olv>rS`7Z^sTz@FbCaD+@KLH7+@K&MZyOQFlU_^T7DiV_YKKDw%oKn#u56++cwx(NC};QPqU%LP6OQw<_}DuHq9DEv57Gg%Q-mMTSq%j8=J)eT0FjNs5irWb%!NMG_9vw2MM;Bhk|p^PGLs*Y|z2P9mn7*2e`z6p79>YymhX;g<V9W_?5V*aUY;Gg0>@%rVpIkzR652-0b(fhKA$8r5mR{6tK$YQHeMH~lpMNg55dA?A^ASEOA`rd~zLfOx919c$_4@mtT2GOXd>fp76xKGC{N0Dbekx*}GcqKcH+yQZ?-+)~L`8jKctdP>8$&_q#TD6l*fYboya3hQ5>mz%W09+Ke<`7U@!XP6$1?{HoqDrX6{x(ttWJMK%T#<oHj=P(taVk1T5$AO3vfq%x{iw5An37tN(G1-ew5No_r7<`M_IZckrU*wDwKpN3OF3?*Y52}6iQ_a48S-%XVW%>Lc^az7t5IU2MgPz7-?G^jzE+>2cM}&CYYO5B$FrlMRWw0Z(%sQyMs;Tf>%kZ;?|I2hP=W_*;DHfFxK$?^A#idDG@ZL)#9=!|Q3qk8@SKpw=u7~WK#;QPE98uU^Cs%v26h*o49>wspee(CX=2&HT34y5c_Cu%R|jKJxcfp?+fw^BBP~NHjEf?>(OGWf7nAy;Ld|#lsqOCSWG<%>MOx3@6-|;CFBUT|w}n#Sky5d5x#vi&(*+L&80(O+Q0fZ~75AR~WA&z%*k#4~RRN~fqwl7b$&()R<y7g=`Z9WCa&$NY&zAI%j|Pdt?174>r#Wn9NbPPrRqXSWz2if*1WJ5!d7Zjv?=2TC=~S<X0##D(#w7FJb@71;kk2G0NJ+a+fi(LWr;3%1gqKpm>SP)cKAs`*ce1iot1TTVj8XER%Ep6eJggc<1W?{SDoH4ix^?YUBchy8ysfjh8R+GS=B~tx1TisbF+S_kn6v5NAF9^jX(SgJIY%UHg&a;L9<j;~h<qLIv|Xu&X7LIyOhCa^)&)r*QVtN3LFLF+4L`!Y9GQE$Fp%%nwaPnG(fW0zNPVIvj4I0u>zwVEij3__t4a^)jJwxHTiVzKNp{8>*1>XK9-3;{8vGxGclv99I{kr9ar`eE?DpnvugU>sEYC~8r+lTKND-50Fv>ES$=8S)&@Chp!43>x<%pACPVPc;O~`R~^*-%Ttw((@aEHZJSa@HT)8baZshE~J%yjRje+V^6#pXn(5ie9aIOp`O>G<gH9iV7L;dMZvp#c}8v9T^%sS4T&h`lTc1o;zYBkvT_oUU?*FiOaG9zwyuFGQiR7~CyKF80eTu3id&P&rX@OyOinO>6vO$^Q8zi0*WVGCXDOay{_gN6tQ5u2k#~7O<?MYu`x&^-uLB5(Klig#9>uTusMvecw`34JE|ABow=*)ZA1sy}-_}eZRPGiL&B~lzD>0TzEqLaJ7g0ViqFX3Y}FnZjzQjS04%2V8ym*<StJx=31yW5PI14n&M0){3OGFD!tdp4IuUGq#EeBQ97H3guZtfLl>_z9#JV{XW{R1A4aNjKoiSIud~^Yt)2@c4F{PIL4-S<gnPctTsc~TF37qL7R5DfWK}XEut!<a?yL?12R-T_UmE5B(CqOBaConX7UyZS=j!Y*LydlFtKFiOTMpA2an)IJ4OY>qI}b*!`J^m_pNeeu#jD?7!ot#G(SN>@gc>xR2XBsihIN;GtvAdpG>#-wWOb8lWfBB#fYoA|rXS_;`Xou(2tEfPtgbkx=qP3uXM+}F#LdGg58!7PHYK*l88I}DzoGSlbMHtaFh{7&iXGP644Is=B5SeuRwipF{zo1@dM1ZA3L}}3JVxsAv+2n+3=zd~)hhneWnww}ff9>$#j}=;ELfvt%WhMgTY@<Z-t$IPtFNqcGD=+BV$^#xX0X}^oP@mv+Zj}I6q{~V+0qin5eG7tVrLFV$_5sY7>ZtU8|Q3aj7vPlsu)0t6?k~8otw;s-wxLj=4B$7>$?>A<ID&}djp;w2MD|rz>P%A_lQ?FdyJINVuGSavaxw3J(Nx*Rdcg5Sm^nK0gOuHcM{c-Al@jlPm6LIQ?L}%m>?=N0#bx~p$*~2Y^u1flWM?J74yYpetT^<q%J~*ibEKAq~{o1-n{lhR?bN5(>9gBh-?x(s8FjKtp{X=W372<SgU(?fgnOJ4+Wh`ggeXYlkt&p)bPks#(#Qo?@9=Kqr`V9@sggdwEX83Z^rA4^_35#1|CugA8v2netL69t}lmxP|*Ql1n%U{uXuSwq%vv}BCMp>5GWocjiJhXP&_N~H%aZ5D25#pyd1p&$|sl81_Qa}QCv@vC*J%bMXU<UGsZnN1o=D)js`^eJFO_+3Ihpo+9ejL#N=lr@Qu;4NNCE0Q7N)z2c8pL5>2r(u|Q~`;6s^>O|dKX(X9nB^hTk+1~*HJ$gQoGUAyZLNt&}5nNA^XS67v0_l|0r=gc{eed*z)29y$BvQTnD8gJHZ5>sX%nlsztd8l_ljD7TA@{vh3OjCjO3(=(PhY2w@18pyiFEDe(+~IL#nu-0<sgOt%fw6Mj)*ncHm~(^G8z98BPpluvQh}7(yYXuS+Muf_-M~^w25Fb+HJAj{g{s^TryV&x7m7p6>|D|}va+yw{%9>oR^)WjWt+QuY0{<__YIo4!}cZkIb6)+KcsnIIK&HKvEZ&2NWO*6(%Rnonyg;oQc$_5syeVm%?^OjMU#L;^75o?L?#lcq~f*3H|EU;h>DiW04&R{VgvZ>{|scg68}8^2ayfnK%BF9D3)}(t`kiMy#t7_Zo0y?OPEs%+&GJhU_)B8rWb|0?0%)92ZnMtD{L`y%>pEDsE2v#+|sKmoTM6VS3gu{dyh$fj*ZpwC^<vMSumU=?2aazi}LdXDrNe~vEro_s~`LxHPqXT@%s}wTERMPUt+%rH;xjAF$==Pd4nk+WaP9=)GIQtgqJIEE0<L~7#_ijI?<Q3n0@UfXJvJgcoM$xhPfPhaV|@ydAGIIP+B~<I;uR<KaIElR_!ZA)|oRS^-b~gwo4tgSUM(vKOhmcXnDh=;+s^^L%2^fr^|BjcO{%7{np?x_rK;6+9j!l+HpPAeT4sZFC82F_?4)FoRW5t`h)U6=q7{O7E2ZNu?hUU@4ZwTMFjKPXf5$PM|k!}eu`#)H>TxU77jMHWFl5R?rg|m`M2pl?R4M&KSHK@w*"

_ACTIONS = json.loads(zlib.decompress(base64.b85decode(_ROUTE_B85)).decode("utf-8"))

_FR_ITEMS = ("MELON", "MILK", "STRAWBERRY", "WOOL")
_WEED_REPLAY_STEPS = 8

# --- v4 herd overlay knobs ---
_HERD_OVERLAY = False   # cow->sheep conversion proved value-neutral locally
_LIQUIDATE = False      # v37b SERVER verdict (08-25): endgame dump fired every game,
                        # zero mirror ties in 65 eps, 1413 vs v33's 1621-at-same-age.
                        # Tie-bank >> $ salvage. Keep OFF unless tie field dies.
_DRAIN_EVERY_TURN = False  # v34 poison: per-turn _shed_drain broke mirror ties
_WHEAT_GUARD = True     # v38 keeps ONLY this wrapper fix (v37a fix #1): rescues
                        # morning wheat buys lost to full-shed per-unit failures.
                        # Moved OUT of the _LIQUIDATE block so it survives alone.
_WOOL_SPLIT = False     # v37b server verdict: no measurable gain, adds divergence
_WOOL_SPLIT_MIN = 16    # only split sells >= this many units
_LIQUIDATE_FROM = 696   # final day only -- do not preempt scheduled premium sales
_IDLE_COLLECT = False   # extra fert sales cannibalize our own 300-unit program's price
_COW_KEEP = 4
_BASE_COWS = 8
_BASE_SHEEP = 4
_FEED_GUARD = False
_FEED_MIN_MULT = 0.5
_FEED_MAX_BUY = 12
_OVERFLOW_AT = 92
_DRAIN_ITEMS = ("WOOL", "STRAWBERRY", "MELON", "MILK")
_WOOL_RESERVE = 2
_FERT_RESERVE = 2       # sell shed fertilizer above this every emission
_FERT_PX_GATE = 55      # stop extra fertilizer sales below this price
_FERT_EXTRA_CAP = 400   # max extra (beyond scheduled program) units to sell

# --- v35 expansion layer (appended crew; base program untouched) ---
_X_ON = False             # master switch
_X_CREW = 2               # extra day-labor hands hired on day 10
_X_HIRE_FROM = 243        # first emission allowed to append crew HIREs (d10 h3)
_X_HIRE_TO = 588          # last emission to hire crew (d24 h12): later days cost
                          # fib-ladder increments of $1.6-4.2k/day and outweigh output
_X_HIRE_MARGIN = 300      # keep this much money after paying the crew wage
_X_TARGET_SHEEP = 0       # extra sheep maintained on _X_PASTURES (0 = none)
_X_LAND_ON = False        # SE land purchase rider
_X_BUY_MONEY_EARLY = 3000 # money gate for sheep buys before _X_BUY_LATE_FROM
_X_BUY_MONEY_LATE = 5000  # money gate afterwards
_X_BUY_LATE_FROM = 336    # emission from which the higher money gate applies (d14)
_X_WHEAT_MIN = 16         # shed wheat floor for (base herd + expansion) daily feed
_X_WHEAT_FROM = 240       # expansion era only (d10+): never compete with base cow buys
_X_WHEAT_MAX_BUY = 12
_X_WHEAT_HOUR = 18        # emission hour for the wheat top-up rider
_X_WHEAT_MONEY = 200
# SE quadrant: the decoded schedule only ever buys NE+SW, so all 25 SE tiles
# are untouched by every base op for the whole season. One appended BUY_LAND
# (~$4k for the third parcel) unlocks 25 virgin tiles next to the shed.
_X_LAND_FROM = 250        # first emission allowed to append BUY_LAND (d10 h10)
_X_LAND_TO = 456          # retry window (through d18 h24)
_X_LAND_MARGIN = 2600     # keep this much money after paying for the land
_X_PASTURES = ((5, 6), (6, 6), (7, 6), (5, 7), (6, 7), (7, 7))  # build order
_X_BLOCK_A = ((5, 6), (6, 6), (7, 6))   # crew hand 0 routine set
_X_BLOCK_B = ((5, 7), (6, 7), (7, 7))   # crew hand 1 routine set
_X_SHED_TILES = ((4, 4), (5, 4), (4, 5), (5, 5))
_X_SHED_PICKUP_A = (5, 5)   # crew hand 0 pickup spot
_X_SHED_PICKUP_B = (4, 5)   # crew hand 1 pickup spot

# --- v39 generator: SE quadrant + tended cow pair (planned continuation) ---
# Server forensics (08-25): winners extend the herd past our d9 freeze via a
# PLANNED d9-13 window (+1-2 animals, P14 seen by d13). Wrapper overlays failed
# 6 ways because appended crews pay marginal fib wages; here the crew is funded
# WAGE-NEUTRALALLY (cut the day's ladder-top base HIREs, re-spend identical fib
# slots) and every op reads LIVE obs state. SE ($4k, LAND_ORDER[2]) is virgin:
# the base schedule only ever owns NW+NE+SW.
_V39_ON = False            # master switch (OFF => byte-identical v38/v33)
_V39_CREW = 2              # tended-cow hands (wage-neutral slots)
_V39_COWS = 2              # extra cows beyond base 8
_V39_LAND_FROM = 250       # first emission allowed to append BUY_LAND (d10 h10)
_V39_LAND_TO = 480         # retry window through d20
_V39_LAND_MARGIN = 3200    # cash floor AFTER paying $4k (base d11+ has income)
_V39_COW_MONEY = 2600      # per-cow cash gate (cow $400 + feed buffer)
_V39_HIRE_FROM = 264       # crew hiring window opens d11 h0
_V39_HIRE_TO = 600         # last emission to hire crew (d25)
_V39_HIRE_MARGIN = 700     # min money after wage bill
_V39_WHEAT_MIN = 18        # shed wheat floor: base 12 feeds + 2 crew cows
_V39_WHEAT_FROM = 264      # expansion era only (d11+)
_V39_WHEAT_MAX_BUY = 10
_V39_FERT_SELL_MIN = 8     # sell shed fertilizer above this many units...
_V39_FERT_PX_MIN = 35      # ...only while price >= this (curve decays to ~$33)
_V39_FERT_SELL_QTY = 4
# Cow blocks in SE (build order): hand A tends row y=6, hand B row y=7.
_V39_PASTURES = ((5, 6), (6, 6), (7, 6), (5, 7), (6, 7), (7, 7))
_V39_BLOCK_A = ((5, 6), (6, 6), (7, 6))
_V39_BLOCK_B = ((5, 7), (6, 7), (7, 7))

_TOWN_INTERVAL = 24   # competition townCenterSellInterval (verified from server replays)
_SHOP_INTERVAL = 4
_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}

_SEATS = {}


def _fresh():
    return {"last_step": -1, "repairs": {}, "due_step": -1, "due": {}, "exec_turn": 0}


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _copy_action(action):
    a = copy.deepcopy(action or {})
    return {
        "farmer": list(a.get("farmer") or ["PASS"]),
        "hands": [list(h or ["PASS"]) for h in (a.get("hands") or [])],
        "market": [list(o) for o in (a.get("market") or [])],
    }


def _align_hands(action, n_hands):
    hands = list(action.get("hands") or [])
    if len(hands) < n_hands:
        hands.extend([["PASS"]] * (n_hands - len(hands)))
    action["hands"] = [list(h or ["PASS"]) for h in hands[:n_hands]]
    return action


def _tile_at(farm, pos):
    try:
        x, y = int(pos[0]), int(pos[1])
        return list(_get(farm, "tiles", []) or [])[y][x]
    except Exception:
        return "LOCKED"


def _trace_unit_action(step, actor_index):
    """Scheduled op for a unit at `step`; actor_index -1 = farmer, >=0 = hand."""
    idx = max(0, min(int(step), len(_ACTIONS) - 1))
    trace = _ACTIONS[idx] or {}
    if actor_index < 0:
        return list(trace.get("farmer") or ["PASS"])
    hands = trace.get("hands") or []
    return list(hands[actor_index] if actor_index < len(hands) else ["PASS"])


def _weed_repair(action, step, seat, farm, sched_idx=0, server_mode=False,
                 n_base_rows=None):
    """DIG weeds blocking scheduled PLANT/BUILD ops, then replay that unit's
    schedule shifted one emission later (repairs delay work by one turn).
    Indices >= n_base_rows belong to the v35 expansion crew -- their ops are
    generated from live state every turn, so scheduled replay would feed them
    stale base-program rows; repairs are never started for them."""
    st = _SEATS[seat]
    repairs = st["repairs"]
    units = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
    acts = [action["farmer"], *action["hands"]]
    # ai space: farmer=0, hand k = k+1. Base hands occupy ai 1..n_base_rows;
    # crew hands start at ai n_base_rows+1.
    crew_floor = len(units) if n_base_rows is None else n_base_rows + 1

    # 1) continue ongoing repairs (unit lost? drop it)
    for ai in sorted(list(repairs)):
        if ai >= len(acts):
            del repairs[ai]
            continue
        age = step - repairs[ai]["start"]
        if age == 1:
            acts[ai] = list(repairs[ai]["intended"])
        elif 2 <= age <= 1 + _WEED_REPLAY_STEPS:
            # Replay the trace from the turn AFTER this repair started.
            base = repairs[ai].get("sched_idx", 0) + (0 if server_mode else 0)
            acts[ai] = _trace_unit_action(base + age - 1, ai - 1)
        else:
            del repairs[ai]

    # 2) start new repairs where the current emission wants to PLANT/BUILD on a weed
    for ai in range(min(len(units), len(acts))):
        if ai in repairs or ai >= crew_floor:
            continue
        intended = acts[ai]
        if not isinstance(intended, list) or not intended:
            continue
        if intended[0] not in ("PLANT", "BUILD_PASTURE", "BUILD_COOP"):
            continue
        tile = _tile_at(farm, units[ai])
        if isinstance(tile, dict) and tile.get("kind") == "WEED":
            repairs[ai] = {"start": step, "intended": list(intended),
                           "sched_idx": int(sched_idx)}
            acts[ai] = ["DIG"]

    action["farmer"] = acts[0]
    action["hands"] = acts[1:]
    return action


def _sell_qty(market, item):
    return sum(
        max(0, int(o[2]))
        for o in market
        if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and o[1] == item
    )


def _future_sell_qty(step, item):
    nxt = int(step) + 1
    if not 0 <= nxt < len(_ACTIONS):
        return 0
    return _sell_qty(_ACTIONS[nxt].get("market") or [], item)


def _town_demand(obs, item, step):
    demand = 1 if (item != "FERTILIZER" and step % _TOWN_INTERVAL == 0) else 0
    if step % _SHOP_INTERVAL != 0:
        return demand
    town = _get(obs, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    for shop in shops:
        products = _SHOP_PRODUCTS.get(str(shop).upper(), ())
        if item in products:
            demand += 2 if len(products) == 1 else 1
    return demand


def _pickup_reserve(action, item):
    reserve = 0
    for op in [action["farmer"], *action["hands"]]:
        if isinstance(op, list) and len(op) >= 2 and op[0] == "PICKUP" and op[1] == item:
            try:
                reserve += max(0, int(op[2])) if len(op) >= 3 else 1
            except Exception:
                reserve += 1
    return reserve


def _apply_repay(action, st, step):
    """Remove quantities previously pulled forward from this turn's sells."""
    if int(st.get("due_step", -1)) != step:
        return action
    due = {str(k): max(0, int(v)) for k, v in dict(st.get("due", {})).items()}
    kept = []
    for o in action["market"]:
        key = str(o[1]) if len(o) >= 3 else ""
        if len(o) >= 3 and o[0] == "SELL" and due.get(key, 0) > 0:
            q = max(0, int(o[2]))
            take = min(q, due[key])
            q -= take
            due[key] -= take
            if q <= 0:
                continue
            o[2] = q
        kept.append(o)
    action["market"] = kept[:10]
    st["due_step"], st["due"] = -1, {}
    return action


def _front_run(action, st, shed, next_market, item_demands, step):
    """Sell part of next turn's premium goods one turn early (bounded by stock)."""
    moved = {}
    for item in _FR_ITEMS:
        target = _sell_qty(next_market, item)
        if target <= 0 or item_demands.get(item, 0) > 0:
            continue
        stock = max(0, int(_get(shed, item, 0) or 0))
        reserve = _pickup_reserve(action, item) + _sell_qty(action["market"], item)
        quantity = min(target, stock - reserve)
        if quantity <= 0:
            continue
        existing = next(
            (o for o in action["market"]
             if len(o) >= 3 and o[0] == "SELL" and o[1] == item),
            None,
        )
        if existing is not None:
            existing[2] = max(0, int(existing[2])) + quantity
        elif len(action["market"]) < 10:
            action["market"].append(["SELL", item, quantity])
        else:
            continue
        moved[item] = moved.get(item, 0) + quantity
    if moved:
        # The deferred quantity must be deducted from the NEXT emission's
        # orders, i.e. when the next obs arrives (step+1) in both modes.
        st["due_step"] = step + 1
        st["due"] = moved
    return action


# ---------------- v4 herd overlay ----------------

def _count_animals(farm):
    n_cow = n_sheep = 0
    for row in list(_get(farm, "tiles", []) or []):
        for c in (row or []):
            if isinstance(c, dict) and "animal" in c:
                if c.get("animal") == "COW": n_cow += 1
                elif c.get("animal") == "SHEEP": n_sheep += 1
    return n_cow, n_sheep


def _herd_overlay(action, st, farm, shed, exec_turn, priv):
    """Retarget the frozen 8C/4S animal program toward 4C/8S using LIVE state:
    obs shed + per-unit inventories are ground truth, so buy->pickup->place
    chains can never desync. Also rescales milk/wool sale programs to the live
    herd so all production clears the shed."""
    n_cow, n_sheep = _count_animals(farm)
    shed_cow = max(0, int(_get(shed, "COW", 0) or 0))
    shed_sheep = max(0, int(_get(shed, "SHEEP", 0) or 0))

    # ---- market: convert surplus scheduled COW buys into SHEEP ----
    room_for_cows = max(0, _COW_KEEP - (n_cow + shed_cow))
    out_mkt = []
    for o in action["market"]:
        if isinstance(o, list) and len(o) >= 3 and o[0] == "BUY_ANIMAL" and o[1] == "COW":
            q = max(0, int(o[2]))
            keep = min(q, room_for_cows)
            conv = q - keep
            room_for_cows -= keep
            if keep > 0:
                out_mkt.append(["BUY_ANIMAL", "COW", keep])
            if conv > 0:
                out_mkt.append(["BUY_ANIMAL", "SHEEP", conv])
            continue
        out_mkt.append(list(o))
    action["market"] = out_mkt[:10]

    # ---- unit ops: flip species based on live shed / unit inventory ----
    invs = list(_get(priv, "inventories", []) or [])

    def _inv_has(inv, item):
        return max(0, int(_get(inv or {}, item, 0) or 0)) > 0

    for ai, uo in enumerate([action["farmer"], *action["hands"]]):
        if not isinstance(uo, list) or len(uo) < 2:
            continue
        inv = invs[ai] if ai < len(invs) else {}
        if uo[0] == "PICKUP" and uo[1] == "COW":
            if shed_cow <= 0 and shed_sheep > 0:
                uo[1] = "SHEEP"
        elif uo[0] == "PLACE" and uo[1] == "COW":
            if not _inv_has(inv, "COW") and _inv_has(inv, "SHEEP"):
                uo[1] = "SHEEP"

    # ---- sales: keep the ORIGINAL sell program untouched -- oversized orders
    # fail harmlessly at the shed; _shed_drain prevents capacity loss. ----
    return action


def _shed_drain(action, shed):
    """Near the shed cap, push extra sell orders so overflow never discards."""
    total = sum(max(0, int(v or 0)) for v in dict(shed or {}).values()
                if isinstance(v, (int, float)))
    if total < _OVERFLOW_AT:
        return action
    for item in _DRAIN_ITEMS:
        if len(action["market"]) >= 10:
            break
        have = max(0, int(_get(shed, item, 0) or 0))
        if have <= 0:
            continue
        existing = next((o for o in action["market"]
                         if len(o) >= 3 and o[0] == "SELL" and o[1] == item), None)
        if existing is None:
            action["market"].append(["SELL", item, have])
    return action


def _idle_collect(action, farm):
    """Free money: hands scheduled to PASS collect fertilizer instead when they
    stand on an animal tile whose fertilizer is ready. No movement required."""
    units = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
    acts = [action["farmer"], *action["hands"]]
    for ai in range(min(len(units), len(acts))):
        op = acts[ai]
        if not isinstance(op, list) or (op and op[0] != "PASS"):
            continue
        tile = _tile_at(farm, units[ai])
        if isinstance(tile, dict) and "animal" in tile and tile.get("fertilizer_available"):
            acts[ai] = ["COLLECT_FERTILIZER"]
    action["farmer"] = acts[0]
    action["hands"] = acts[1:]
    return action


def _fert_outlet(action, shed, exec_turn, st):
    """Sell collected surplus fertilizer only while the price holds up.
    Dumping hundreds of units depresses the linear price curve ($0.20/unit)
    and cannibalizes our scheduled program's revenue -- so cap the extra
    volume and stop when price falls below the gate."""
    px = st.get("fert_px")
    if px is None:
        return action
    if int(px) < _FERT_PX_GATE:
        return action
    sold = st.get("fert_extra", 0)
    room = _FERT_EXTRA_CAP - sold
    if room <= 0:
        return action
    have = max(0, int(_get(shed, "FERTILIZER", 0) or 0))
    add = min(have - _FERT_RESERVE, room, 24)
    if add <= 0:
        return action
    existing = next((o for o in action["market"]
                     if len(o) >= 3 and o[0] == "SELL" and o[1] == "FERTILIZER"), None)
    if existing is not None:
        existing[2] = max(int(existing[2]), add)
    elif len(action["market"]) < 10:
        action["market"].append(["SELL", "FERTILIZER", add])
    else:
        return action
    st["fert_extra"] = sold + add
    return action


def _feed_guard(action, farm, shed, exec_turn):
    """Once a day near dusk, top up shed wheat so the bigger herd never starves."""
    if exec_turn % _TOWN_INTERVAL != 18:
        return action
    n_cow, n_sheep = _count_animals(farm)
    n_anim = n_cow + n_sheep
    if n_anim == 0 or len(action["market"]) >= 10:
        return action
    wheat = max(0, int(_get(shed, "WHEAT", 0) or 0))
    if wheat >= n_anim * _FEED_MIN_MULT:
        return action
    buy = min(_FEED_MAX_BUY, max(0, n_anim * 2 - wheat))
    if buy > 0:
        action["market"].append(["BUY_PRODUCT", "WHEAT", buy])
    return action


def _shed_headroom(shed, cap=100):
    total = sum(max(0, int(v or 0)) for v in dict(shed or {}).values()
                if isinstance(v, (int, float)))
    return max(0, cap - total)


def _wheat_guard(action, farm, shed, exec_turn):
    """v37a fix #1: the >=1.32.4 engine makes BUY_PRODUCT fail per-unit while
    the shed is at capacity. The schedule's morning wheat buys fire right after
    the overnight auto-drop fills the shed and silently vanish (measured in
    server replays: d16/d26 buys lost while feeding drains 15+ that day).
    Remedy: when a buy-bearing emission opens with <2 free slots, front-load
    sells of items this same emission was going to sell later anyway (list
    order => our sells commit before our buys), then re-queue the buys."""
    if _shed_headroom(shed) >= 2:
        return action
    mkt = [o for o in (action.get("market") or []) if isinstance(o, list) and o]
    buys = [o for o in mkt if o[0] == "BUY_PRODUCT" or o[0] == "BUY_SEED"]
    if not buys:
        return action
    sells = [(i, o) for i, o in enumerate(mkt) if o[0] == "SELL"]
    if not sells:
        return action
    keep = {id(o) for _, o in sells}
    others = [o for o in mkt if id(o) not in keep]
    # largest quantities first: more slots freed per order
    sells.sort(key=lambda t: -max(0, int(t[1][2])) if len(t[1]) >= 3 else 1)
    rebuilt = [o for _, o in sells] + others + buys[: 10 - len(sells)]
    action["market"] = rebuilt[:10]
    return action


def _wool_split(action, st, shed, exec_turn):
    """v37b fix #2: the wool price curve is steep near market I0, so a big
    same-emission dump walks the quote down unit by unit. Defer half to the
    next emission (town consumption recovers the price in between). Skipped
    on turns where _front_run already moved premium goods (no stacking)."""
    # 1) repay wool deferred from the previous emission
    if int(st.get("due2_step", -1)) == int(exec_turn):
        add = max(0, int(st.get("due2", 0) or 0))
        st["due2_step"], st["due2"] = -1, 0
        stock = max(0, int(_get(shed, "WOOL", 0) or 0))
        add = min(add, stock)
        if add > 0:
            ex = next((o for o in action["market"]
                       if len(o) >= 3 and o[0] == "SELL" and o[1] == "WOOL"), None)
            if ex is not None:
                ex[2] = max(0, int(ex[2])) + add
            elif len(action["market"]) < 10:
                action["market"].append(["SELL", "WOOL", add])
    # 2) split this emission's oversized wool sell
    if st.get("due_step") == int(exec_turn) + 1 and st.get("due"):
        return action  # front-run active this turn; keep identity
    ex = next((o for o in action["market"]
               if len(o) >= 3 and o[0] == "SELL" and o[1] == "WOOL"), None)
    if ex is None:
        return action
    q = max(0, int(ex[2]))
    if q < _WOOL_SPLIT_MIN:
        return action
    half = q // 2
    ex[2] = q - half
    st["due2_step"] = int(exec_turn) + 1
    st["due2"] = half
    return action


def _endgame_liquidate(action, shed, exec_turn):
    """Final day: dump everything sellable -- dead inventory earns zero.
    Restricted to the last day so scheduled sales keep their premium timing."""
    if exec_turn < _LIQUIDATE_FROM:
        return action
    for item in ("WOOL", "MILK", "STRAWBERRY", "MELON", "FERTILIZER"):
        if len(action["market"]) >= 10:
            break
        have = max(0, int(_get(shed, item, 0) or 0))
        if have <= 0:
            continue
        existing = next((o for o in action["market"]
                         if len(o) >= 3 and o[0] == "SELL" and o[1] == item), None)
        if existing is not None:
            existing[2] = max(int(existing[2]), have)
        else:
            action["market"].append(["SELL", item, have])
    return action


# ---------------- v35 expansion layer ----------------
# Appended day-labor crew + 6 extra sheep on dedicated SW pastures. The base
# program's rows/orders are never modified: crew HIREs are appended after the
# last base market order (tail hand indices bind to tail rows), and crew unit
# ops overwrite only rows past the base row count. All decisions read LIVE obs
# (shed, inventories, tile flags) so drift self-corrects.

def _x_tile(farm, x, y):
    try:
        return list(_get(farm, "tiles", []) or [])[y][x]
    except Exception:
        return "LOCKED"


def _x_animals_on(farm, wanted):
    out = {}
    for y, row in enumerate(list(_get(farm, "tiles", []) or [])):
        for x, c in enumerate(row or []):
            if isinstance(c, dict) and "animal" in c and c["animal"] == "SHEEP" \
                    and (x, y) in wanted:
                out[(x, y)] = c
    return out


def _x_empty_pastures(farm):
    n = 0
    for row in list(_get(farm, "tiles", []) or []):
        for c in (row or []):
            if isinstance(c, dict) and c.get("kind") == "PASTURE" and "animal" not in c:
                n += 1
    return n


def _x_built(farm):
    n = 0
    for (px, py) in _X_PASTURES:
        c = _x_tile(farm, px, py)
        if isinstance(c, dict) and c.get("kind") == "PASTURE":
            n += 1
    return n


def _x_step(pos, tgt):
    dx, dy = tgt[0] - pos[0], tgt[1] - pos[1]
    if dx:
        return ["EAST"] if dx > 0 else ["WEST"]
    if dy:
        return ["SOUTH"] if dy > 0 else ["NORTH"]
    return ["PASS"]


def _fib(n):
    a, b = 1, 1
    for _ in range(int(max(0, n))):
        a, b = b, a + b
    return a


def _x_crew_row(ci, pos, farm, priv, inv, shed, idx):
    """Decide one crew hand's op. Priority: place carried sheep > URGENT feed
    (escape imminent) > refill wheat > feed > care > harvest > fetch new
    sheep > build (hand0) > pass. Keeping installed animals alive always
    outranks fetching replacements."""
    block = _X_BLOCK_A if ci == 0 else _X_BLOCK_B
    pickup_spot = _X_SHED_PICKUP_A if ci == 0 else _X_SHED_PICKUP_B
    mine = _x_animals_on(farm, set(block))

    def inv_qty(item):
        return max(0, int(_get(inv or {}, item, 0) or 0))

    def empty_own_pasture():
        for (px, py) in block:
            c = _x_tile(farm, px, py)
            if isinstance(c, dict) and c.get("kind") == "PASTURE" and "animal" not in c:
                return (px, py)
        return None

    # 1) carry a sheep to its pasture
    if inv_qty("SHEEP") > 0:
        tgt = empty_own_pasture()
        if tgt is not None:
            return ["PLACE", "SHEEP"] if pos == tgt else _x_step(pos, tgt)

    # 2) rescue: any of my sheep one missed meal from escaping
    if inv_qty("WHEAT") > 0:
        for p, c in mine.items():
            if int(c.get("consecutive_unfed", 0) or 0) >= 1:
                return ["FEED"] if pos == p else _x_step(pos, p)

    # 3) refill wheat if any of my sheep still needs feeding today
    need_feed = any(not c.get("fed_today") for c in mine.values())
    if need_feed and inv_qty("WHEAT") == 0 \
            and max(0, int(_get(shed, "WHEAT", 0) or 0)) > 0:
        if pos == pickup_spot:
            return ["PICKUP", "WHEAT", 4]
        return _x_step(pos, pickup_spot)

    # 4) routine feed / care / harvest on my block
    for p, c in mine.items():
        if not c.get("fed_today") and inv_qty("WHEAT") > 0:
            return ["FEED"] if pos == p else _x_step(pos, p)
    for p, c in mine.items():
        if not c.get("cared_today"):
            return ["CARE"] if pos == p else _x_step(pos, p)
    for p, c in mine.items():
        if int(c.get("yield_units", 0) or 0) > 0:
            return ["HARVEST"] if pos == p else _x_step(pos, p)

    # 5) fetch a sheep from the shed: whoever arrives first takes the next one
    if max(0, int(_get(shed, "SHEEP", 0) or 0)) >= 1 and empty_own_pasture() is not None:
        if pos == pickup_spot:
            return ["PICKUP", "SHEEP", 1]
        return _x_step(pos, pickup_spot)

    # 6) builder (hand0 only): expand the pasture staircase
    if ci == 0 and _x_built(farm) < len(_X_PASTURES):
        for (px, py) in _X_PASTURES:
            c = _x_tile(farm, px, py)
            if isinstance(c, dict) and c.get("kind") == "WEED":
                return ["DIG"] if pos == (px, py) else _x_step(pos, (px, py))
            if c is None:
                return ["BUILD_PASTURE"] if pos == (px, py) else _x_step(pos, (px, py))
    return ["PASS"]


def _x_expand(action, st, obs, farm, idx, n_base_rows):
    priv = _get(obs, "private", {}) or {}
    shed = _get(priv, "shed", {}) or {}
    money = int(_get(farm, "money", 0) or 0)
    hour = idx % 24
    day = idx // 24

    # ---- market riders ----
    # Never compete with the base program's own capital orders this turn:
    # squeezing cash under a queued BUY_SEED/BUY_ANIMAL makes THAT order fail,
    # which shifts hand indices and desyncs the whole base program.
    base_capital_pending = any(
        isinstance(o, list) and o and o[0] in ("BUY_SEED", "BUY_ANIMAL", "BUY_LAND")
        for o in action["market"])
    # sheep buys: retry daily until the target herd stands on our pastures
    my_sheep = len(_x_animals_on(farm, set(_X_PASTURES)))
    pending = max(0, int(_get(shed, "SHEEP", 0) or 0))
    for inv in list(_get(priv, "inventories", []) or []):
        pending += max(0, int(_get(inv or {}, "SHEEP", 0) or 0))
    gate = _X_BUY_MONEY_LATE if idx >= _X_BUY_LATE_FROM else _X_BUY_MONEY_EARLY
    if _X_TARGET_SHEEP > 0 and my_sheep + pending < _X_TARGET_SHEEP \
            and money >= gate \
            and _x_built(farm) > 0 and not base_capital_pending \
            and len(action["market"]) < 10:
        action["market"].append(["BUY_ANIMAL", "SHEEP", 1])

    # wheat logistics: total herd demand = base FEED ops (~12/day) + expansion
    # (~6-8/day). Only active in the EXPANSION ERA (day 10+): earlier, the
    # base program self-manages and -- critical lesson -- squeezing cash here
    # bounces the base schedule's own $400-per-cow purchases (permanently
    # losing the animals). Fire every turn while below target; commits cannot
    # fail once queued (cash -> shed).
    if idx >= _X_WHEAT_FROM and money >= _X_WHEAT_MONEY \
            and max(0, int(_get(shed, "WHEAT", 0) or 0)) < _X_WHEAT_MIN \
            and len(action["market"]) < 10:
        need = _X_WHEAT_MIN - max(0, int(_get(shed, "WHEAT", 0) or 0))
        action["market"].append(
            ["BUY_PRODUCT", "WHEAT", min(_X_WHEAT_MAX_BUY, max(need, 4) + 4)])

    # expansion wool outlet: the base sell program is sized for 4 sheep, so
    # our extra ~50% wool production accumulates and eventually chokes the
    # shed to cap (EOD drop then DISCARDS base milk/berries). Sell surplus in
    # small bursts under real shed pressure -- wool price impact is minor
    # because the base program itself already drives wool past I0 on sale days.
    total_shed = sum(max(0, int(v or 0)) for v in dict(shed or {}).values()
                     if isinstance(v, (int, float)))
    wool = max(0, int(_get(shed, "WOOL", 0) or 0))
    if idx >= _X_WHEAT_FROM and total_shed >= 55 and wool >= 6 \
            and len(action["market"]) < 10:
        action["market"].append(["SELL", "WOOL", min(wool - 4, 12)])

    # fourth land parcel (SE): the base schedule buys NE (d6) and SW (d10),
    # so from d10 on we hold 3 parcels and SE is purchasable for $4k
    # (LAND_PRICES[2]) -- 25 virgin tiles next to the shed.
    unlocked = list(_get(farm, "unlocked_quadrants", []) or [])
    if _X_LAND_ON and _X_LAND_FROM <= idx <= _X_LAND_TO and len(unlocked) == 3 \
            and money >= (1000, 2000, 4000)[len(unlocked) - 1] + _X_LAND_MARGIN \
            and len(action["market"]) < 10:
        action["market"].append(["BUY_LAND"])

    # crew hires: retried each turn until affordable, every day from day 10 on;
    # appended AFTER all base orders so base wage costs stay untouched. We
    # record the live hand count at fire time: those next-spawning hands are
    # exactly the crew (spawn order = execution order), immune to base hires
    # failing elsewhere in the queue.
    # crew hires -- WAGE-NEUTRAL FUNDING (the core v36 idea): the fib ladder
    # charges by TOTAL hires/day, so we don't append (that inflates every
    # later hire). Instead, at the day's FIRST hire-bearing emission we cut
    # the _X_CREW ladder-top (most expensive, lowest-seniority) base hires
    # and re-spend those identical fib slots on flock-tending hands. The
    # day's total hire count -- and the whole wage bill -- matches base
    # exactly; the crew is paid out of reallocated slots, not new money.
    mkt_q = action["market"]
    base_hires = sum(1 for o in mkt_q if o and o[0] == "HIRE")
    if (_X_HIRE_FROM <= idx <= _X_HIRE_TO and hour <= 2
            and int(st.get("x_hire_day", -1)) != day
            and base_hires >= _X_CREW
            and money >= _X_HIRE_MARGIN + 700
            and len(mkt_q) <= 10):
        cut = 0
        for i in range(len(mkt_q) - 1, -1, -1):
            if cut >= _X_CREW:
                break
            if mkt_q[i] and mkt_q[i][0] == "HIRE":
                del mkt_q[i]
                cut += 1
        st["x_crew_idx"] = len(list(_get(farm, "hands", []) or [])) \
            + sum(1 for o in mkt_q if o and o[0] == "HIRE")
        st["x_crew_n"] = _X_CREW
        st["x_hire_day"] = day
        for _ in range(_X_CREW):
            action["market"].append(["HIRE"])

    # ---- crew unit rows (at the indices recorded when the crew spawned) ----
    hands_live = list(_get(farm, "hands", []) or [])
    invs = list(_get(priv, "inventories", []) or [])
    c_start = int(st.get("x_crew_idx", -1))
    c_n = int(st.get("x_crew_n", 0) or 0)
    if c_start >= 0 and c_n > 0:
        for ci in range(c_n):
            hi = c_start + ci
            if hi >= len(hands_live):
                continue  # not spawned (yet)
            pos = tuple(hands_live[hi])
            # inventories[0] = farmer; hand k's inventory = inventories[k+1]
            inv = invs[hi + 1] if hi + 1 < len(invs) else {}
            while len(action["hands"]) <= hi:
                action["hands"].append(["PASS"])
            action["hands"][hi] = _x_crew_row(ci, pos, farm, priv, inv, shed, idx)
    return action


# ------------------------- v39 generator layer -------------------------

def _v39_animals_on(farm, wanted):
    out = {}
    for y, row in enumerate(list(_get(farm, "tiles", []) or [])):
        for x, c in enumerate(row or []):
            if isinstance(c, dict) and "animal" in c and c["animal"] == "COW" \
                    and (x, y) in wanted:
                out[(x, y)] = c
    return out


def _v39_built(farm):
    n = 0
    for (px, py) in _V39_PASTURES:
        c = _x_tile(farm, px, py)
        if isinstance(c, dict) and c.get("kind") == "PASTURE":
            n += 1
    return n


def _v39_cow_row(ci, pos, farm, priv, inv, shed, idx):
    """One crew hand's op over its SE cow block. Priority: place carried cow >
    rescue feed (escape imminent) > refill wheat > feed > care > harvest >
    fetch cow > build (hand0) > gather fertilizer > pass."""
    block = _V39_BLOCK_A if ci == 0 else _V39_BLOCK_B
    pickup_spot = (5, 5) if ci == 0 else (4, 5)
    mine = _v39_animals_on(farm, set(block))

    def inv_qty(item):
        return max(0, int(_get(inv or {}, item, 0) or 0))

    def empty_own_pasture():
        for (px, py) in block:
            c = _x_tile(farm, px, py)
            if isinstance(c, dict) and c.get("kind") == "PASTURE" and "animal" not in c:
                return (px, py)
        return None

    # 1) carry a cow to its pasture
    if inv_qty("COW") > 0:
        tgt = empty_own_pasture()
        if tgt is not None:
            return ["PLACE", "COW"] if pos == tgt else _x_step(pos, tgt)

    # 2) rescue: any of my cows one missed meal from escaping
    if inv_qty("WHEAT") > 0:
        for p, c in mine.items():
            if int(c.get("consecutive_unfed", 0) or 0) >= 1:
                return ["FEED"] if pos == p else _x_step(pos, p)

    # 3) refill wheat if any of my cows still needs feeding today
    need_feed = any(not c.get("fed_today") for c in mine.values())
    if need_feed and inv_qty("WHEAT") == 0 \
            and max(0, int(_get(shed, "WHEAT", 0) or 0)) > 0:
        if pos == pickup_spot:
            return ["PICKUP", "WHEAT", 4]
        return _x_step(pos, pickup_spot)

    # 4) routine feed / care / harvest on my block (care banks +1/day bonus)
    for p, c in mine.items():
        if not c.get("fed_today") and inv_qty("WHEAT") > 0:
            return ["FEED"] if pos == p else _x_step(pos, p)
    for p, c in mine.items():
        if not c.get("cared_today"):
            return ["CARE"] if pos == p else _x_step(pos, p)
    for p, c in mine.items():
        if int(c.get("yield_units", 0) or 0) > 0:
            return ["HARVEST"] if pos == p else _x_step(pos, p)

    # 5) fetch a cow from the shed when one of my pastures stands empty
    if max(0, int(_get(shed, "COW", 0) or 0)) >= 1 and empty_own_pasture() is not None:
        if pos == pickup_spot:
            return ["PICKUP", "COW", 1]
        return _x_step(pos, pickup_spot)

    # 6) builder (hand0 only): expand the SE staircase. Pre-purchase, SE tiles
    #    are the string "LOCKED" -- skip them (never path onto them).
    if ci == 0 and _v39_built(farm) < len(_V39_PASTURES):
        for (px, py) in _V39_PASTURES:
            c = _x_tile(farm, px, py)
            if c == "LOCKED":
                continue
            if isinstance(c, dict) and c.get("kind") == "WEED":
                return ["DIG"] if pos == (px, py) else _x_step(pos, (px, py))
            if c is None:
                return ["BUILD_PASTURE"] if pos == (px, py) else _x_step(pos, (px, py))

    # 7) idle: gather available fertilizer (keep inventory headroom for wheat)
    if inv_qty("WHEAT") == 0 and inv_qty("FERTILIZER") < 3:
        for p, c in mine.items():
            if c.get("fertilizer_available"):
                return ["COLLECT_FERTILIZER"] if pos == p else _x_step(pos, p)
    return ["PASS"]


def _v39_expand(action, st, obs, farm, idx):
    """Market riders + crew rows for the planned SE continuation. Every rider
    is gated so it can never squeeze cash under a queued base capital order."""
    priv = _get(obs, "private", {}) or {}
    shed = _get(priv, "shed", {}) or {}
    money = int(_get(farm, "money", 0) or 0)
    hour = idx % 24
    day = idx // 24
    unlocked = list(_get(farm, "unlocked_quadrants", []) or [])

    base_capital_pending = any(
        isinstance(o, list) and o and o[0] in ("BUY_SEED", "BUY_ANIMAL", "BUY_LAND")
        for o in action["market"])

    # ---- market riders ----
    # SE land ($4k, LAND_ORDER[2]): base already owns NE+SW (len==3) by d10,
    # so SE is the NEXT parcel -- fire on len==3. (Seed-trace lesson: gating
    # on len==2 never fires; the base makes its own SW purchase at d10 h0.)
    if _V39_LAND_FROM <= idx <= _V39_LAND_TO and len(unlocked) == 3 \
            and money >= 4000 + _V39_LAND_MARGIN \
            and not base_capital_pending \
            and len(action["market"]) < 10 \
            and int(st.get("v39_land_day", -1)) != day:
        action["market"].append(["BUY_LAND"])
        st["v39_land_day"] = day

    # cows: buy toward target once SE is LIVE (len==4) and a pasture exists.
    se_live = len(unlocked) >= 4
    my_cows = len(_v39_animals_on(farm, set(_V39_PASTURES)))
    pending = max(0, int(_get(shed, "COW", 0) or 0))
    for inv in list(_get(priv, "inventories", []) or []):
        pending += max(0, int(_get(inv or {}, "COW", 0) or 0))
    if se_live and my_cows + pending < _V39_COWS \
            and money >= _V39_COW_MONEY \
            and _v39_built(farm) > 0 and not base_capital_pending \
            and len(action["market"]) < 10:
        action["market"].append(["BUY_ANIMAL", "COW", 1])

    # wheat logistics for the enlarged herd. DEFUSED after seed-1 trace: fire
    # only on a REAL deficit below the base's own operating floor, never
    # against base capital orders, never near shed cap (EOD discard risk).
    total_shed_pre = sum(max(0, int(v or 0)) for v in dict(shed or {}).values()
                         if isinstance(v, (int, float)))
    if idx >= _V39_WHEAT_FROM and not base_capital_pending \
            and money >= 3000 and total_shed_pre <= 88 \
            and max(0, int(_get(shed, "WHEAT", 0) or 0)) < 12 \
            and len(action["market"]) < 10:
        need = 14 - max(0, int(_get(shed, "WHEAT", 0) or 0))
        action["market"].append(["BUY_PRODUCT", "WHEAT", min(6, max(need, 2))])

    # fertilizer outlet: the base program collects far less than it could;
    # sell surplus above reserve while the quote is still worth taking
    mkt = _get(obs, "market", {}) or {}
    prices = _get(mkt, "prices", {}) or {}
    px_fert = prices.get("FERTILIZER") if isinstance(prices, dict) else None
    fert = max(0, int(_get(shed, "FERTILIZER", 0) or 0))
    if fert > _FERT_RESERVE and (px_fert is None or int(px_fert) >= _V39_FERT_PX_MIN) \
            and len(action["market"]) < 10:
        qty = min(fert - _FERT_RESERVE, _V39_FERT_SELL_QTY)
        if qty > 0:
            action["market"].append(["SELL", "FERTILIZER", qty])

    # milk outlet: base SELL quantities are FIXED, sized for 8 cows. Our 2
    # extra cows (+care bonuses) outproduce that program, so surplus piles up
    # and dies at the shed cap. Sell above a working floor, plus bursts under
    # real shed pressure (same logic that keeps the expansion flock liquid).
    milk = max(0, int(_get(shed, "MILK", 0) or 0))
    total_shed = sum(max(0, int(v or 0)) for v in dict(shed or {}).values()
                     if isinstance(v, (int, float)))
    if len(action["market"]) < 10 and \
            ((milk > 26 and day >= 13) or (total_shed >= 58 and milk >= 6)):
        qty = min(milk - 4 if milk > 26 else milk - 2, 16)
        if qty > 0:
            action["market"].append(["SELL", "MILK", qty])

    # crew hires -- APPENDED (v39 revision): the fib ladder charges by TOTAL
    # hires that day, so insertion point is wage-irrelevant; cutting base
    # hires instead deletes their FEED/WATER labor (v36 lesson, re-proven in
    # seed-1 trace). Appended pair costs only the marginal fib slots.
    mkt_q = action["market"]
    if (_V39_HIRE_FROM <= idx <= _V39_HIRE_TO and hour <= 2
            and int(st.get("v39_hire_day", -1)) != day
            and money >= _V39_HIRE_MARGIN + 700
            and len(mkt_q) <= 9
            and len(unlocked) >= 4):
        st["v39_crew_idx"] = len(list(_get(farm, "hands", []) or [])) \
            + sum(1 for o in mkt_q if o and o[0] == "HIRE")
        st["v39_crew_n"] = _V39_CREW
        st["v39_hire_day"] = day
        for _ in range(_V39_CREW):
            action["market"].append(["HIRE"])

    # ---- crew unit rows at recorded indices ----
    hands_live = list(_get(farm, "hands", []) or [])
    invs = list(_get(priv, "inventories", []) or [])
    c_start = int(st.get("v39_crew_idx", -1))
    c_n = int(st.get("v39_crew_n", 0) or 0)
    if c_start >= 0 and c_n > 0:
        for ci in range(c_n):
            hi = c_start + ci
            if hi >= len(hands_live):
                continue  # not spawned yet
            pos = tuple(hands_live[hi])
            inv = invs[hi + 1] if hi + 1 < len(invs) else {}
            while len(action["hands"]) <= hi:
                action["hands"].append(["PASS"])
            action["hands"][hi] = _v39_cow_row(ci, pos, farm, priv, inv, shed, idx)
    return action


def _stan_agent(obs):
    try:
        raw_step = _get(obs, "step", None)
        server_mode = raw_step is None          # Kaggle server omits `step`
        if server_mode:
            day = int(_get(obs, "day", 0) or 0)
            hour = int(_get(obs, "hour", 0) or 0)
            step = day * _TOWN_INTERVAL + hour
        else:
            step = int(raw_step or 0)

        seat = _seat(obs)
        st = _SEATS.get(seat)
        if st is None or step < int(st.get("last_step", -1)) or step == 0:
            _SEATS[seat] = _fresh()
            st = _SEATS[seat]
        st["last_step"] = step
        if 0 <= int(st.get("due_step", -1)) < step and st["due_step"] != step:
            st["due_step"], st["due"] = -1, {}

        # Schedule index of THIS emission. Calibrated on server replays: on the
        # Kaggle server, the response to the obs labelled turn t executes at
        # replay turn t+1 (turn 0 is a discarded warm-up call), so the schedule
        # must be advanced by one; the local library harness is 1:1.
        idx = min(step + 1, len(_ACTIONS) - 1) if server_mode \
            else min(step, len(_ACTIONS) - 1)
        st["exec_turn"] = step + 1 if server_mode else step

        farm = _farm(obs, seat)
        n_hands = len(list(_get(farm, "hands", []) or []))

        action = _copy_action(_ACTIONS[idx])
        if server_mode and step == 0:
            # Turn 0 is consumed by Kaggle's warm-up call, so the schedule's
            # opening market program would never fire. Fold it into our first
            # live emission (turn 1), keeping the turn-1 field ops.
            opening = _ACTIONS[0]
            merged = [list(o) for o in (opening.get("market") or [])]
            for o in (action.get("market") or []):
                if len(merged) >= 10:
                    break
                merged.append(list(o))
            action["market"] = merged[:10]
        elif server_mode and step == 1:
            deferred = [list(o) for o in (_ACTIONS[1].get("market") or [])]
            merged = deferred + [list(o) for o in (action.get("market") or [])]
            action["market"] = merged[:10]

        action = _align_hands(action, n_hands)
        n_base_rows = len(_ACTIONS[min(idx, len(_ACTIONS) - 1)].get("hands") or []) \
            if _X_ON else None
        action = _weed_repair(action, step, seat, farm, idx, server_mode, n_base_rows)
        action = _align_hands(action, n_hands)

        if _HERD_OVERLAY:
            shed_now = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
            priv = _get(obs, "private", {}) or {}
            action = _herd_overlay(action, st, farm, shed_now, st["exec_turn"], priv)
            if _FEED_GUARD:
                action = _feed_guard(action, farm, shed_now, st["exec_turn"])
        if _IDLE_COLLECT:
            action = _idle_collect(action, farm)
        if _LIQUIDATE:
            shed_now2 = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
            if _DRAIN_EVERY_TURN:
                action = _shed_drain(action, shed_now2)
            action = _endgame_liquidate(action, shed_now2, st["exec_turn"])
        if _WHEAT_GUARD:
            # v38: independent of _LIQUIDATE (guard is identity-preserving in
            # mirror games -- it only fires when the emission already carries
            # buys AND the shed is full, where base buys would fail anyway).
            shed_now2 = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
            action = _wheat_guard(action, farm, shed_now2, st["exec_turn"])
        if _X_ON:
            action = _x_expand(action, st, obs, farm, st["exec_turn"], n_base_rows)
        if _V39_ON:
            action = _v39_expand(action, st, obs, farm, st["exec_turn"])

        # Premium market lead: look at the NEXT emission's sells; skip items the
        # town demands on the turn this sale will actually execute.
        nxt = _ACTIONS[min(idx + 1, len(_ACTIONS) - 1)]
        shed = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
        demands = {item: _town_demand(obs, item, st["exec_turn"]) for item in _FR_ITEMS}
        action = _apply_repay(action, st, step)
        if _WOOL_SPLIT:
            action = _wool_split(action, st, shed, st["exec_turn"])
        action = _front_run(action, st, shed, nxt.get("market") or [], demands, step)
        if _IDLE_COLLECT:
            # last: capped fertilizer outlet only uses slots the premium
            # program left free; gated on live price to avoid self-cannibalization
            st["fert_px"] = ((shed.get("market") or {}) if isinstance(shed, dict) else {}).get("FERTILIZER") \
                or (_get(_get(obs, "market", {}) or {}, "prices", {}) or {}).get("FERTILIZER")
            action = _fert_outlet(action, shed, st["exec_turn"], st)
        return _align_hands(action, n_hands)
    except Exception:
        try:
            n_hands = len(list(_get(_farm(obs, _seat(obs)), "hands", []) or []))
        except Exception:
            n_hands = 0
        return {"farmer": ["PASS"], "hands": [["PASS"]] * n_hands, "market": []}


# ==============================================================================
# v68 Grandmaster Wrapper Stack
# ==============================================================================

_ELASTICITY = {
    "MELON": 3.6,
    "WOOL": 3.2,
    "MILK": 1.6,
    "STRAWBERRY": 1.6,
    "CARROT": 0.7,
    "TOMATO": 0.6,
    "FERTILIZER": 0.4,
    "EGG": 0.2,
    "WHEAT": 0.2,
}
_FRAGILE_ITEMS = ("MELON", "WOOL", "MILK", "STRAWBERRY")
_SELLABLE = ("MELON", "WOOL", "MILK", "STRAWBERRY", "FERTILIZER", "TOMATO", "CARROT", "EGG", "WHEAT")
_TERMINAL_FLUSH_START = 712
_TERMINAL_LAST_DROP = 718


def _shed_dist(pos):
    x, y = int(pos[0]), int(pos[1])
    dx = 0 if 4 <= x <= 5 else (4 - x if x < 4 else x - 5)
    dy = 0 if 4 <= y <= 5 else (4 - y if y < 4 else y - 5)
    return dx + dy


def _move_to_shed(pos):
    x, y = int(pos[0]), int(pos[1])
    if x < 4:
        return ["EAST"]
    if x > 5:
        return ["WEST"]
    if y < 4:
        return ["SOUTH"]
    if y > 5:
        return ["NORTH"]
    return ["DROP"]


def _worker_terminal_action(pos, inv, tile, step, default_act):
    dist = _shed_dist(pos)
    total_load = sum(int(v) for v in inv.values() if isinstance(v, (int, float)) and v > 0)
    tile_yield = int(tile.get("yield_units", 0) or 0) if isinstance(tile, dict) else 0
    if dist == 0:
        if total_load > 0:
            return ["DROP"]
        return default_act
    if total_load > 0 and step + dist >= _TERMINAL_LAST_DROP:
        return _move_to_shed(pos)
    if tile_yield > 0 and step + dist + 1 <= _TERMINAL_LAST_DROP:
        return ["HARVEST"]
    if total_load > 0:
        return _move_to_shed(pos)
    return default_act


def _dollar_impact(item, qty, price):
    try:
        p = float(price)
    except (ValueError, TypeError):
        p = 1.0
    return max(0, int(qty or 0)) * p * _ELASTICITY.get(item, 1.0)


_FRAGILE_MIN_PRICE = 2.0
_FEED_SKIP_START = 384
_FEED_SKIP_END = 712


def _v67_tile_at(tiles, pos):
    try:
        x, y = int(pos[0]), int(pos[1])
    except (ValueError, TypeError, IndexError):
        return None
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        tile = tiles[y][x]
        return tile if isinstance(tile, dict) else None
    return None


def _skip_neg_ev_cow_feed(action, obs, step, milk_px, wheat_px):
    """Skip negative-EV cow feeding on deep-glut boards (escape-proof).

    1 wheat/day/cow -> ~1.1 milk/day. When milk is crashed ($1) and wheat is at
    ceiling ($40-50), each feeding burns ~$45 of wheat for ~$1 of milk. Skipping
    every other day halves that burn. The consecutive_unfed < 1 guard guarantees
    animals are never unfed twice in a row (2 consecutive unfed days = escape).
    Sheep are never gated (wool is premium on exactly these boards).
    """
    if not (_FEED_SKIP_START <= step < _FEED_SKIP_END):
        return action
    is_mid_glut = (step < 672 and milk_px <= 6.0 and wheat_px >= 35.0)
    is_late_neg_ev = (step >= 672 and milk_px <= 30.0 and wheat_px >= 25.0)
    if not (is_mid_glut or is_late_neg_ev):
        return action

    seat = 1 if int(obs.get("player", 0) or 0) == 1 else 0
    farms = list(obs.get("farms", []) or [])
    farm = farms[seat] if seat < len(farms) else {}
    tiles = list(farm.get("tiles", []) or [])
    if not tiles:
        return action

    def gate(act_list, pos):
        if not act_list or act_list[0] != "FEED":
            return act_list
        tile = _v67_tile_at(tiles, pos)
        if tile is None or tile.get("animal") != "COW":
            return act_list
        try:
            unfed = int(tile.get("consecutive_unfed", 0) or 0)
        except (ValueError, TypeError):
            unfed = 0
        if unfed >= 1:
            return act_list
        return ["PASS"]

    result = copy.deepcopy(action or {})
    f_pos = farm.get("farmer") or [4, 4]
    result["farmer"] = gate(list(result.get("farmer") or ["PASS"]), f_pos)

    hands_act = [list(h or ["PASS"]) for h in (result.get("hands") or [])]
    hands_pos = farm.get("hands") or []
    for idx, h_act in enumerate(hands_act):
        if idx < len(hands_pos):
            hands_act[idx] = gate(h_act, hands_pos[idx])
    result["hands"] = hands_act
    return result


_TRIAGE_START = 240
_TRIAGE_END = 712
_TRIAGE_SHED_AT = 88
_TRIAGE_RESERVE = 1
_TRIAGE_MAX_ORDERS = 2
_TRIAGE_QTY = 4
_TRIAGE_ITEMS = ("MILK", "STRAWBERRY", "WHEAT", "CARROT", "TOMATO", "EGG", "MELON", "WOOL")


def _suppress_low_ev_fertilizer(action, obs):
    prices = (obs.get("market") or {}).get("prices") or {}
    try:
        fert_price = float(prices.get("FERTILIZER", 100) or 100)
    except (ValueError, TypeError):
        fert_price = 100.0

    fallback = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
    step = int(obs.get("step", fallback) if obs.get("step") is not None else fallback)
    is_day29 = (step >= 696)
    suppress_fert = (fert_price <= 1.0)

    if not suppress_fert and not is_day29:
        return action

    seat = 1 if int(obs.get("player", 0) or 0) == 1 else 0
    farms = list(obs.get("farms", []) or [])
    farm = farms[seat] if seat < len(farms) else {}
    tiles = list(farm.get("tiles", []) or [])

    result = copy.deepcopy(action or {})

    if is_day29 and result.get("market"):
        filtered_market = []
        for order in result["market"]:
            if isinstance(order, (list, tuple)) and order:
                cmd = order[0]
                if cmd in ("BUY_SEED", "BUY_ANIMAL", "BUY_LAND"):
                    continue
                if cmd == "BUY_PRODUCT" and len(order) >= 2 and order[1] == "FERTILIZER":
                    continue
            filtered_market.append(order)
        result["market"] = filtered_market

    farmer_act = list(result.get("farmer") or [])
    if farmer_act and farmer_act[0] == "COLLECT_FERTILIZER" and (suppress_fert or is_day29):
        f_pos = farm.get("farmer") or [4, 4]
        fx, fy = int(f_pos[0]), int(f_pos[1])
        tile = tiles[fy][fx] if 0 <= fy < len(tiles) and 0 <= fx < len(tiles[fy]) else None
        if isinstance(tile, dict) and int(tile.get("yield_units", 0) or 0) > 0:
            result["farmer"] = ["HARVEST"]

    hands_act = [list(h or ["PASS"]) for h in (result.get("hands") or [])]
    hands_pos = farm.get("hands") or []
    for idx, h_act in enumerate(hands_act):
        if h_act and h_act[0] == "COLLECT_FERTILIZER" and (suppress_fert or is_day29):
            if idx < len(hands_pos):
                hx, hy = int(hands_pos[idx][0]), int(hands_pos[idx][1])
                tile = tiles[hy][hx] if 0 <= hy < len(tiles) and 0 <= hx < len(tiles[hy]) else None
                if isinstance(tile, dict) and int(tile.get("yield_units", 0) or 0) > 0:
                    hands_act[idx] = ["HARVEST"]
    result["hands"] = hands_act
    return result


def _apply_terminal_liquidation(action, obs, step):
    if step < _TERMINAL_FLUSH_START:
        return action
    result = copy.deepcopy(action or {})
    seat = 1 if int(obs.get("player", 0) or 0) == 1 else 0
    farms = list(obs.get("farms", []) or [])
    farm = farms[seat] if seat < len(farms) else {}
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    prices = (obs.get("market") or {}).get("prices") or {}
    inventories = private.get("inventories") or []
    tiles = list(farm.get("tiles", []) or [])
    f_pos_raw = farm.get("farmer") or [4, 4]
    farmer_pos = (int(f_pos_raw[0]), int(f_pos_raw[1]))
    farmer_inv = inventories[0] if len(inventories) > 0 else {}
    hands_pos = farm.get("hands") or []

    fx, fy = farmer_pos
    f_tile = tiles[fy][fx] if 0 <= fy < len(tiles) and 0 <= fx < len(tiles[fy]) else None
    result["farmer"] = _worker_terminal_action(farmer_pos, farmer_inv, f_tile, step, list(result.get("farmer") or ["PASS"]))

    hands_act = list(result.get("hands") or [])
    while len(hands_act) < len(hands_pos):
        hands_act.append(["PASS"])
    for h_idx, h_pos_raw in enumerate(hands_pos):
        h_pos = (int(h_pos_raw[0]), int(h_pos_raw[1]))
        h_inv = inventories[h_idx + 1] if len(inventories) > h_idx + 1 else {}
        hx, hy = h_pos
        h_tile = tiles[hy][hx] if 0 <= hy < len(tiles) and 0 <= hx < len(tiles[hy]) else None
        orig_act = list(hands_act[h_idx] or ["PASS"])
        hands_act[h_idx] = _worker_terminal_action(h_pos, h_inv, h_tile, step, orig_act)
    result["hands"] = hands_act

    dropped = {}
    if result.get("farmer") == ["DROP"]:
        for it, count in farmer_inv.items():
            if it in _SELLABLE:
                dropped[it] = dropped.get(it, 0) + max(0, int(count or 0))
    for h_idx, h_pos_raw in enumerate(hands_pos):
        if h_idx < len(hands_act) and hands_act[h_idx] == ["DROP"]:
            h_inv = inventories[h_idx + 1] if len(inventories) > h_idx + 1 else {}
            for it, count in h_inv.items():
                if it in _SELLABLE:
                    dropped[it] = dropped.get(it, 0) + max(0, int(count or 0))

    if step in (713, 714, 715):
        cands = []
        for item in _FRAGILE_ITEMS:
            qty = int(shed.get(item, 0) or 0) + dropped.get(item, 0)
            if qty > 0:
                try:
                    p = float(prices.get(item, 1) or 1)
                except (ValueError, TypeError):
                    p = 1.0
                if p <= _FRAGILE_MIN_PRICE:
                    continue
                cands.append((_dollar_impact(item, qty, p), qty * p, item, qty))
        cands.sort(key=lambda x: (x[0], x[1]), reverse=True)
        fragile_sells = [["SELL", item, qty] for _, _, item, qty in cands]

        if len(fragile_sells) < 10:
            fragile_items_sold = set(item for _, _, item, _ in cands)
            other_cands = []
            for item in _SELLABLE:
                if item not in fragile_items_sold:
                    qty = int(shed.get(item, 0) or 0) + dropped.get(item, 0)
                    if qty > 0:
                        try:
                            p = float(prices.get(item, 1) or 1)
                        except (ValueError, TypeError):
                            p = 1.0
                        if p <= _FRAGILE_MIN_PRICE and item in _FRAGILE_ITEMS:
                            continue
                        other_cands.append((_dollar_impact(item, qty, p), qty * p, item, qty))
            other_cands.sort(key=lambda x: (x[0], x[1]), reverse=True)
            backfill_sells = [["SELL", item, qty] for _, _, item, qty in other_cands]
            result["market"] = (fragile_sells + backfill_sells)[:10]
        else:
            existing = [
                o for o in (action.get("market") or [])
                if not (isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL" and o[1] in _FRAGILE_ITEMS)
            ]
            result["market"] = (fragile_sells + existing)[:10]

    elif step >= 716:
        cands = []
        for item in _SELLABLE:
            qty = int(shed.get(item, 0) or 0) + dropped.get(item, 0)
            if qty > 0:
                try:
                    p = float(prices.get(item, 1) or 1)
                except (ValueError, TypeError):
                    p = 1.0
                cands.append((_dollar_impact(item, qty, p), qty * p, item, qty))
        if cands:
            cands.sort(key=lambda x: (x[0], x[1]), reverse=True)
            result["market"] = [["SELL", item, qty] for _, _, item, qty in cands[:10]]
        else:
            result["market"] = list(action.get("market") or [])

    return result


def agent(obs, configuration=None):
    fallback = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
    step = int(obs.get("step", fallback) if obs.get("step") is not None else fallback)
    obs["step"] = step

    act = _stan_agent(obs)
    if step == 0:
        return act

    px = (obs.get("market") or {}).get("prices") or {}
    try:
        milk_px = float(px.get("MILK", 160) or 160)
    except (ValueError, TypeError):
        milk_px = 160.0
    try:
        wheat_px = float(px.get("WHEAT", 25) or 25)
    except (ValueError, TypeError):
        wheat_px = 25.0
    try:
        wool_px = float(px.get("WOOL", 200) or 200)
    except (ValueError, TypeError):
        wool_px = 200.0

    # 1. EV-Gated Feed Gate:
    # Days 16-27 (step >= 384 and step < 672): Only suppresses if milk is deeply crashed (<= $6)
    # and wheat is near ceiling (>= $35), preventing false-alarm cow starvation while capturing
    # savings when milk is truly dead ($1).
    # Days 28-29 (step >= 672): Suppresses if milk <= $30 and wheat >= $25.
    is_mid_glut = (384 <= step < 672 and milk_px <= 6.0 and wheat_px >= 35.0)
    is_late_neg_ev = (step >= 672 and milk_px <= 30.0 and wheat_px >= 25.0)
    if is_mid_glut or is_late_neg_ev:
        act["market"] = [
            o for o in (act.get("market") or [])
            if not (isinstance(o, (list, tuple)) and len(o) >= 2 and o[0] == "BUY_PRODUCT" and o[1] == "WHEAT")
        ]

    # 2. Clone Detection: Compare live balance and hand count
    seat = 1 if int(obs.get("player", 0) or 0) == 1 else 0
    farms = list(obs.get("farms", []) or [])
    my_farm = farms[seat] if seat < len(farms) else {}
    opp_farm = farms[1 - seat] if (1 - seat) < len(farms) else {}

    is_clone = (
        abs(float(opp_farm.get("money", 0) or 0) - float(my_farm.get("money", 0) or 0)) < 1.0
        and len(opp_farm.get("hands", []) or []) == len(my_farm.get("hands", []) or [])
    )

    # 3. Clone-Gated High-EV Surge Monetization (step < 712)
    # In mirror play (is_clone == True), stays completely dormant to preserve 100% mirror ties
    if not is_clone and step < 712:
        priv = obs.get("private") or {}
        shed = priv.get("shed") or {}
        current_orders = list(act.get("market") or [])
        slots_left = 10 - len(current_orders)

        # A. Peak Wool Exploitation: when wool is high and shed has surplus stock
        shed_wool = max(0, int(shed.get("WOOL", 0) or 0))
        if slots_left > 0 and wool_px >= 160.0 and shed_wool >= 2:
            sell_wool_qty = min(shed_wool - 1, 4)
            if sell_wool_qty > 0:
                current_orders.append(["SELL", "WOOL", sell_wool_qty])
                slots_left -= 1

        # B. Peak Milk Exploitation: when milk surges and shed has surplus stock
        shed_milk = max(0, int(shed.get("MILK", 0) or 0))
        if slots_left > 0 and milk_px >= 180.0 and shed_milk >= 3:
            sell_milk_qty = min(shed_milk - 1, 6)
            if sell_milk_qty > 0:
                current_orders.append(["SELL", "MILK", sell_milk_qty])
                slots_left -= 1

        # C. Shed-Cap Triage: when the shed is near cap, dump the cheapest
        # produce into free slots so premium inflow (wool/milk) is never lost
        # to EOD cap discard. Additive only: never alters schedule orders, so
        # the stan front-run/repay accounting is untouched. Cheapest-first
        # protects premium goods; FERTILIZER excluded (program price).
        if slots_left > 0 and _TRIAGE_START <= step < _TRIAGE_END:
            try:
                shed_total = sum(max(0, int(v or 0)) for v in shed.values())
            except (ValueError, TypeError):
                shed_total = 0
            if shed_total >= _TRIAGE_SHED_AT:
                priced = []
                for item in _TRIAGE_ITEMS:
                    try:
                        q = max(0, int(shed.get(item, 0) or 0))
                    except (ValueError, TypeError):
                        q = 0
                    if q > _TRIAGE_RESERVE:
                        try:
                            p = float(px.get(item, 1) or 1)
                        except (ValueError, TypeError):
                            p = 1.0
                        priced.append((p, item, q))
                priced.sort(key=lambda x: x[0])
                added = 0
                for p, item, q in priced:
                    if slots_left <= 0 or added >= _TRIAGE_MAX_ORDERS:
                        break
                    qty = min(q - _TRIAGE_RESERVE, _TRIAGE_QTY)
                    if qty > 0:
                        current_orders.append(["SELL", item, qty])
                        slots_left -= 1
                        added += 1

        act["market"] = current_orders

    act = _suppress_low_ev_fertilizer(act, obs)
    act = _skip_neg_ev_cow_feed(act, obs, step, milk_px, wheat_px)
    return _apply_terminal_liquidation(act, obs, step)


def kaggle_submission_agent(obs, configuration=None):
    return agent(obs, configuration)


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
