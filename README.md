## Complete Workflow

### Phase 1: Core Processing
1. **Input**  
   Coordinator provides `video_list.csv`:
   ```csv
   title,date
   "Works of Righteousness - Part 3","2-26-25"
   "Foundation of Faith Q&A","3-05-25"
   ```

2. **Automated Processing**  
   ```bash
   python run_pipeline.py --input video_list.csv
   ```
   - Matches YouTube videos (93% accuracy threshold)
   - Processes audio to podcast standards
   - Outputs to `output/podcasts/`

3. **Quality Assurance**  
   Manual verification of:
   - Audio quality
   - Metadata accuracy
   - Chapter markers
   - Duration matching

### Phase 2: Podcast Scheduling

1. **Scheduling Input**  
   After QA, receive WhatsApp message format:
   ```text
  Will you please set up the new wine skin part 1 & 2 for tomorrow 1-15-25 and I'll get the rest of the list done tomorrow. Thanks Paul!
   ```

2. **AI-Powered Parsing**  
   Groq LLM converts message to structured data:
   ```json
   {
     "entries": [
       {
         "title": "New Wine Skin - Part 1",
         "schedule_date": "2025-01-25"
       },
       {
         "title": "New Wine Skin - Part 2", 
         "schedule_date": "2025-01-25"
       }
     ]
   }
   ```

3. **Schedule Publishing**  
   ```bash
   python scripts/schedule_podbean.py \
     --message input/whatsapp_message.txt \
     --audio-dir output/podcasts
   ```
   - Matches titles to processed audio files
   - Sets Pacific Timezone schedule
   - Validates against Podbean API

## Scheduling Configuration

### Required in `.env`:
```ini
GROQ_API_KEY=your_groq_key
PODBEAN_CLIENT_ID=your_client_id
PODBEAN_CLIENT_SECRET=your_secret
YOUTUBE_API_KEY=your_youtube_key
```

## WhatsApp Message Rules

The parser handles:
- Mixed date formats (MM-DD-YY, MM/DD/YYYY, etc)
- Relative dates ("tomorrow", "next Tuesday")
- Varied punctuation and line breaks
- Multiple titles per line
- Informal requests mixed with scheduling info