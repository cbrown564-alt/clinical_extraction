import Image from "next/image";
import s from "./introImagery.module.css";

export default function DemoIllustration({ name, alt, portrait = false, hero = false }: { name: string; alt: string; portrait?: boolean; hero?: boolean }) {
  const src = `/demo/imagery/${name}.png`;
  const wide = /^research-(extract|decide|overview)-v\d+$/.test(name);
  return <a className={s.imageLink} href={src} target="_blank" rel="noreferrer" aria-label={`${alt} Open full-size illustration in a new tab.`}>
    <Image src={src} alt={alt} width={portrait ? 1122 : wide ? 1774 : 1536} height={portrait ? 1402 : wide ? 887 : 1024} sizes={portrait ? "(max-width: 900px) 90vw, 380px" : hero ? "(max-width: 760px) 90vw, 600px" : "(max-width: 760px) 95vw, 1200px"} preload={hero} className={s.image} />
  </a>;
}
