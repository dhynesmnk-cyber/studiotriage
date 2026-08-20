## Visual Identity: "The Field Journal"
The UI must feel like a high-end, tactile archival notebook. Elegant, polished, bespoke.

## Tailwind CSS Configuration
- **Colors**: 
  - Background: `stone-50` or `neutral-100` (warm off-white, like thick paper).
  - Text: `stone-800` (soft black, never pure `#000000`).
  - Accents/Borders: `stone-300` (subtle pencil lines).
  - Highlights: `amber-700` or `emerald-800` (ink-like accents for approved states).
- **Typography**:
  - Headings: Serif (e.g., `font-serif`, 'Lora' or 'Playfair Display'). Gives an editorial, curated feel.
  - Body/UI: Clean Sans (e.g., `font-sans`, 'Inter' or 'System UI'). Highly legible for logs.
  - Monospace: 'JetBrains Mono' for file paths and technical logs.

## Layout Rules
- **Split Screen**: 40% width Left (Original), 60% width Right (AI Draft). Separated by a subtle 1px `stone-300` border.
- **Cards/Panes**: No heavy drop shadows. Use subtle 1px borders and very faint background tints (`bg-stone-100/50`) to create depth.
- **Interactions**: HTMX loading states should use a subtle "ink bleeding" or "typewriter" skeleton loader, not a spinning circle.
- **PIN Modal**: Centered, blurred backdrop, heavy serif typography for the prompt ("Authorize Execution").
