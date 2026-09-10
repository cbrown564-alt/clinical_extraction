import Image from "next/image";
import s from "./applicationStories.module.css";

export default function ApplicationIcon({ kind }: { kind: "cohort" | "longitudinal" | "prediction" }) {
  return <Image className={s.applicationIcon} src={`/demo/imagery/application-${kind}-icon-v1.png`} alt="" width={32} height={32} sizes="32px" />;
}
