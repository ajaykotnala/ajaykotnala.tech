# Redesign Tinder System Design Page

Redesign [tinder-system-design.html](file:///Users/ajaykotnala/Desktop/myfolder/mywork/Portfolio/ajaykotnala.tech/tinder-system-design.html) to match the light Apple-inspired theme from [index.html](file:///Users/ajaykotnala/Desktop/myfolder/mywork/Portfolio/ajaykotnala.tech/index.html), replace architecture diagrams with Excalidraw-style hand-drawn SVGs, and adopt a Medium-like article layout.

## Proposed Changes

### 1. Theme Overhaul: Dark → Light (Apple Design System)

Replace the current dark color palette with the index.html design tokens:

| Token | Current (Dark) | New (Light) |
|-------|---------------|-------------|
| Background | `#0a0e1a` | `#ffffff` |
| Secondary BG | `#141925` | `#f5f5f7` (parchment) |
| Text Primary | `#e4e6eb` | `#1d1d1f` |
| Text Secondary | `#9ca3af` | `#86868b` |
| Accent | `#00d4aa` (teal) | `#0066cc` (Apple Blue) |
| Borders | `#2a3441` | `rgba(0,0,0,0.08)` |
| Tinder accent | `#fd5068` / `#ff7854` | Kept for brand identity in callouts |

### 2. Navigation: Match Index.html Double-Nav

Replace the current dark floating nav with the index.html's **Apple double navigation** pattern:
- **Global Nav**: Fixed 44px black bar with logo + social icons
- **Sub Nav**: Frosted sticky 52px bar with article title + "Back to Portfolio" button

### 3. Medium-Friendly Article Layout

- Increase article width from `820px` → `680px` (Medium uses ~700px for optimal readability)
- Use `Georgia` / system serif for article body text (Medium's signature feel)
- Keep `Inter` for headings and UI elements
- Increase line-height to `1.9` for body text
- Larger font size: `20px` body text (Medium standard)
- Add drop cap styling for first paragraph of each section
- Add estimated read time with a clap/bookmark bar at the bottom
- Subtle left-side progress indicator

### 4. Excalidraw-Style Architecture Diagrams

Replace all 3 SVG diagrams with **Excalidraw-style hand-drawn aesthetics**:

- **Rough/sketchy stroke style**: Use SVG `filter` with `feTurbulence` for wobbly edges
- **Hand-drawn font**: Use "Virgil" (Excalidraw's font) via Google Fonts or fallback to `Comic Neue` / cursive
- **Light background**: White/cream canvas with subtle dot grid pattern
- **Pastel colors**: Soft fills instead of dark solid fills (light blue `#e3f2fd`, light pink `#fce4ec`, light green `#e8f5e9`)
- **Rough connectors**: Arrow lines with slight hand-drawn wobble using SVG path noise

Diagrams to redesign:
1. **Diagram 1** — High-Level System Architecture (Client → Gateway → Services → DBs)
2. **Diagram 2** — The "Lost Match" Race Condition (timeline/sequence)
3. **Diagram 3** — Pre-Computed Feed Generation Pipeline

### 5. Component Restyling

#### Callout Boxes
- White background with left colored border (keep tinder pink/orange for warning/insight)
- Light shadow instead of dark card

#### Code Blocks
- Light syntax theme (GitHub-style light)
- White background with subtle border

#### Entity Cards
- White cards with subtle shadows on hover (Apple store-utility-card style)
- Remove dark fills

#### Comparison Tables
- Clean white with `#f5f5f7` header rows
- Thin divider lines

#### Scale Stats
- Apple-style number display with blue gradient accent
- White card with soft shadow

#### Deep Dive Accordions
- White card with light border
- Blue accent for toggle icon

#### Level Cards (Mid/Senior/Staff)
- White background with colored top border
- Matching index.html's `store-utility-card` pattern

### 6. Footer

Match index.html footer:
- `#f5f5f7` parchment background
- Clean social links row
- Fine print copyright

---

## File Modified

#### [MODIFY] [tinder-system-design.html](file:///Users/ajaykotnala/Desktop/myfolder/mywork/Portfolio/ajaykotnala.tech/tinder-system-design.html)

Complete restyling of CSS variables, all component styles, navigation, SVG diagrams, and footer.

## Verification Plan

### Manual Verification
- Open the redesigned page in browser to verify visual consistency with index.html
- Check all 3 architecture diagrams render correctly with Excalidraw hand-drawn style
- Verify responsive behavior on mobile breakpoints
- Confirm all interactive elements (accordions, scroll progress, TOC links) still work
- Compare side-by-side with index.html to ensure cohesive theme
