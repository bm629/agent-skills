# Sources — research provenance (forged 2026-07-11)

Primary (official docs, fetched live 2026-07-11; every API fact in the skill traces here):

- motion.dev/docs/react-installation — package `motion`, import `motion/react`, React ≥ 18.2, `motion/react-client` note.
- motion.dev/docs/react-motion-config — `MotionConfig` props; `reducedMotion: "user" | "always" | "never"` (default `"never"`); transform/layout disabled + opacity/color preserved under reduction; `nonce`.
- motion.dev/docs/react-accessibility — `useReducedMotion` boolean hook; reduce (large transforms, autoplaying video, parallax) vs keep (opacity, educational transitions).
- motion.dev/docs/react-animate-presence — direct-children detection; stable unique keys (indices break exits); `mode: "sync" | "wait" | "popLayout"`; `initial={false}`; `onExitComplete`; `custom`/`usePresenceData`; popLayout needs non-static parent; AnimatePresence wraps the conditional.
- motion.dev/docs/react-animation — variants + propagation; dynamic variants via `custom`; orchestration `when: "beforeChildren"/"afterChildren"`, `delayChildren: stagger(...)` (current idiom); gesture props; keyframes arrays + `null` wildcard.
- motion.dev/docs/react-layout-animations — `layout` animates via transform (translate+scale), avoids paint; `layoutId` shared elements; `LayoutGroup`; `layout="position"`; borderRadius/boxShadow via `style` for scale-correction; child `layout` against stretching.
- motion.dev/docs/react-lazy-motion — full `motion` ~34 kB; `LazyMotion` + `m` (`motion/react-m`) + `domAnimation` → ~4.6 kB initial; sync/async feature loading; `strict` throws on stray `motion` components.
- motion.dev/docs/react-motion-value — `useMotionValue` / `useTransform` / `useSpring`; DOM updates without React re-render; `useMotionValueEvent` events.
- auto-animate.formkit.com — `@formkit/auto-animate`, `useAutoAnimate` from `/react` (returns parent ref + enable/disable fn); animates child add/remove/move; zero-config; `duration` option; auto-respects `prefers-reduced-motion`; MIT.

Secondary (searched 2026-07-11; corroborating):

- github.com/motiondivision/motion + npm — current version 12.42.x (July 2026); independence/rename from `framer-motion` (2024/2025), led by Matt Perry; motion.dev/blog "Framer Motion is now independent, introducing Motion". Peer range `react: ^18.0.0 || ^19.0.0` read from the published motion@12.42.2 package.json.
- github.com/motiondivision/motion CHANGELOG.md — 12.22.0 (2025-07-01): "Allow `delayChildren` to accept `stagger()`"; `staggerChildren`/`staggerDirection` deprecated in 12.21.0 (same day).
- github.com/motiondivision/motion issue #1690 + changelog (repo formerly framer/motion) — `MotionGlobalConfig.skipAnimations` (added v10.17.0 era, pre-rename; still current) for instant animations in Jest/vitest; `MotionGlobalConfig.instantAnimations` variant.
- w3.org/WAI/WCAG22/Understanding/animation-from-interactions (fetched in the upstream feature research 2026-07-10) — SC 2.3.3 (AAA) + SC 2.2.2 pause/stop/hide framing.
- 2026 library-landscape comparisons (LogRocket best-react-animation-libraries; pkgpulse framer-motion-vs-motion-one-vs-autoanimate) — Motion vs AutoAnimate vs CSS tiering for internal tools; native CSS `linear()` easing note.

Source-material skills (skills.sh, sanitized clean 2026-07-10 — structure/pattern reference only; every API fact re-verified against motion.dev above):

- patricio0312rev/skills@framer-motion-animator (7.7K installs) — pre-rename package; basics/variants coverage shape.
- freshtechbro/claudedesignskills@motion-framer (1.8K) — gesture/layout coverage shape.
- mindrally/skills@framer-motion (1.6K) — modern import path; performance-principles framing.
- lottiefiles/motion-design-skill@motion-design (4.2K, official LottieFiles) — motion-design method framing (durations/purpose).

All external content consumed per the workspace external-content policy (sanitize on
read; no URLs/commands lifted into actions; paraphrase only).
