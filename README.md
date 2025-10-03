# Constitution Q&A API - Complete Integration Guide

## Installation

```bash
pip install flask flask-cors sentence-transformers faiss-cpu \
langchain langchain-openai python-dotenv PyMuPDF python-docx nltk
```

## Postman Testing Guide

### 1. Upload Document

**Method:** `POST`  
**URL:** `http://localhost:5000/upload`  
**Body Type:** `form-data`

**Form Data:**
- Key: `file` (Type: File)
  - Select your Constitution PDF/DOCX
- Key: `user_id` (Type: Text)
  - Value: `user123` (or any unique identifier)

**Response:**
```json
{
  "user_id": "user123",
  "message": "Document processed successfully",
  "metadata": {
    "filename": "constitution_of_kenya.pdf",
    "upload_date": "2025-10-03T10:30:00",
    "total_chunks": 245
  }
}
```

**What Happens:**
- Document is uploaded to `uploads/` folder
- Text extracted from PDF/DOCX
- Text cleaned and split into ~300-word chunks
- Chunks embedded using sentence transformers
- FAISS index created for fast semantic search
- User can now ask questions

---

### 2. Ask Questions

**Method:** `POST`  
**URL:** `http://localhost:5000/ask`  
**Headers:** `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "user_id": "user123",
  "question": "What are the fundamental rights and freedoms?"
}
```

**Response:**
```json
{
  "question": "What are the fundamental rights and freedoms?",
  "answer": "According to Chapter 4 of the Constitution, fundamental rights and freedoms include:\n\n1. **Right to Life** - Every person has the right to life\n2. **Freedom of Expression** - Including freedom of artistic creativity, academic freedom, and freedom of scientific research\n3. **Right to Property** - Every person has the right to own property\n4. **Freedom of Association** - Including freedom to form, join or participate in political parties\n\nThese rights are protected under Articles 26-48 and are subject to limitations only as prescribed by law.",
  "sources": [
    {
      "text": "Chapter 4 - The Bill of Rights: Every person has the right to life. The right to life begins at conception...",
      "relevance": 0.87
    }
  ]
}
```

**Sample Questions to Test:**
- "What is the structure of government?"
- "How is the President elected?"
- "What are the functions of Parliament?"
- "How can the constitution be amended?"
- "What are the devolution principles?"

---

### 3. Generate Summary

**Method:** `POST`  
**URL:** `http://localhost:5000/summary`  
**Headers:** `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "user_id": "user123"
}
```

**Response:**
```json
{
  "summary": "**EXECUTIVE SUMMARY**\n\nThe Constitution of Kenya 2010 is the supreme law...\n\n**KEY PROVISIONS**\n\n*Rights and Freedoms*\nChapter 4 establishes comprehensive bill of rights...\n\n*Government Structure*\nEstablishes a presidential system with separation of powers...",
  "filename": "constitution_of_kenya.pdf",
  "chunks_analyzed": 50,
  "total_chunks": 245
}
```

---

### 4. Download Summary

**Method:** `POST`  
**URL:** `http://localhost:5000/download_summary`  
**Headers:** `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "user_id": "user123",
  "summary": "**EXECUTIVE SUMMARY**\n\nThe Constitution of Kenya..."
}
```

**Response:**
- Downloads DOCX file: `summary_constitution_of_kenya_20251003.docx`
- Formatted document with headings, paragraphs, metadata

**Postman Note:** To test download:
1. Click "Send and Download"
2. File will be saved to your Downloads folder

---

### 5. Get Document Info

**Method:** `GET`  
**URL:** `http://localhost:5000/documents/user123`

**Response:**
```json
{
  "filename": "constitution_of_kenya.pdf",
  "chunks": ["chunk1...", "chunk2..."],
  "upload_date": "2025-10-03T10:30:00",
  "total_chunks": 245
}
```

---

### 6. Delete Document

**Method:** `DELETE`  
**URL:** `http://localhost:5000/documents/user123`

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

---

## Frontend Integration Examples

### React Example

```javascript
// 1. Upload Document
const uploadDocument = async (file, userId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', userId);
  
  const response = await fetch('http://localhost:5000/upload', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};

// 2. Ask Question
const askQuestion = async (userId, question) => {
  const response = await fetch('http://localhost:5000/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, question })
  });
  
  return await response.json();
};

// 3. Generate Summary
const generateSummary = async (userId) => {
  const response = await fetch('http://localhost:5000/summary', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId })
  });
  
  return await response.json();
};

// 4. Download Summary
const downloadSummary = async (userId, summary) => {
  const response = await fetch('http://localhost:5000/download_summary', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, summary })
  });
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'constitution_summary.docx';
  a.click();
};

// Usage in Component
function ConstitutionApp() {
  const [userId] = useState('user123');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [summary, setSummary] = useState(null);
  
  const handleUpload = async (e) => {
    const file = e.target.files[0];
    const result = await uploadDocument(file, userId);
    alert(result.message);
  };
  
  const handleAsk = async () => {
    const result = await askQuestion(userId, question);
    setAnswer(result);
  };
  
  const handleSummary = async () => {
    const result = await generateSummary(userId);
    setSummary(result.summary);
  };
  
  const handleDownload = async () => {
    await downloadSummary(userId, summary);
  };
  
  return (
    <div>
      <input type="file" onChange={handleUpload} accept=".pdf,.docx" />
      
      <input 
        value={question} 
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={handleAsk}>Ask</button>
      
      {answer && (
        <div>
          <h3>Answer:</h3>
          <p>{answer.answer}</p>
        </div>
      )}
      
      <button onClick={handleSummary}>Generate Summary</button>
      {summary && <button onClick={handleDownload}>Download Summary</button>}
    </div>
  );
}
```

### Vue.js Example

```vue
<template>
  <div class="constitution-app">
    <!-- Upload -->
    <input type="file" @change="uploadDocument" accept=".pdf,.docx" />
    
    <!-- Q&A -->
    <div class="qa-section">
      <input v-model="question" placeholder="Ask about the constitution..." />
      <button @click="askQuestion">Ask</button>
      
      <div v-if="answer" class="answer">
        <h3>Answer:</h3>
        <p>{{ answer.answer }}</p>
      </div>
    </div>
    
    <!-- Summary -->
    <button @click="generateSummary">Generate Summary</button>
    <button v-if="summary" @click="downloadSummary">Download Summary</button>
    
    <div v-if="summary" class="summary">
      <pre>{{ summary }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userId: 'user123',
      question: '',
      answer: null,
      summary: null
    };
  },
  methods: {
    async uploadDocument(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', this.userId);
      
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      alert(result.message);
    },
    
    async askQuestion() {
      const response = await fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.userId,
          question: this.question
        })
      });
      
      this.answer = await response.json();
    },
    
    async generateSummary() {
      const response = await fetch('http://localhost:5000/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: this.userId })
      });
      
      const result = await response.json();
      this.summary = result.summary;
    },
    
    async downloadSummary() {
      const response = await fetch('http://localhost:5000/download_summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.userId,
          summary: this.summary
        })
      });
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'constitution_summary.docx';
      a.click();
    }
  }
};
</script>
```

### Angular Example

```typescript
// constitution.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class ConstitutionService {
  private baseUrl = 'http://localhost:5000';
  
  constructor(private http: HttpClient) {}
  
  uploadDocument(file: File, userId: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    return this.http.post(`${this.baseUrl}/upload`, formData);
  }
  
  askQuestion(userId: string, question: string) {
    return this.http.post(`${this.baseUrl}/ask`, { user_id: userId, question });
  }
  
  generateSummary(userId: string) {
    return this.http.post(`${this.baseUrl}/summary`, { user_id: userId });
  }
  
  downloadSummary(userId: string, summary: string) {
    return this.http.post(`${this.baseUrl}/download_summary`, 
      { user_id: userId, summary },
      { responseType: 'blob' }
    );
  }
}

// constitution.component.ts
export class ConstitutionComponent {
  userId = 'user123';
  question = '';
  answer: any;
  summary: string;
  
  constructor(private service: ConstitutionService) {}
  
  onUpload(event: any) {
    const file = event.target.files[0];
    this.service.uploadDocument(file, this.userId).subscribe(
      result => alert('Document uploaded successfully')
    );
  }
  
  onAsk() {
    this.service.askQuestion(this.userId, this.question).subscribe(
      result => this.answer = result
    );
  }
  
  onGenerateSummary() {
    this.service.generateSummary(this.userId).subscribe(
      (result: any) => this.summary = result.summary
    );
  }
  
  onDownload() {
    this.service.downloadSummary(this.userId, this.summary).subscribe(
      blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'constitution_summary.docx';
        a.click();
      }
    );
  }
}
```

---

## User Flow Example

### Typical User Journey

1. **Landing Page**
   - User sees upload area: "Upload Constitution Document"
   - Drag-and-drop or click to select PDF/DOCX
   - Upload button triggers `/upload`

2. **Processing Feedback**
   - Loading spinner: "Processing document..."
   - Success message: "Document ready! You can now ask questions."
   - Show metadata: "245 sections indexed"

3. **Question Interface**
   - Chat-like interface
   - Input box: "Ask anything about the constitution..."
   - Previous questions/answers displayed above
   - Each answer shows relevance sources

4. **Summary Generation**
   - Button: "Generate Full Summary"
   - Loading: "Analyzing entire document... (30-60s)"
   - Display formatted summary
   - Download button appears

5. **Download**
   - Click "Download Summary"
   - DOCX file downloads with formatted content
   - Includes title, date, all sections

---

## Error Handling

### Common Errors & Solutions

**Error: "Document not found"**
```json
{ "error": "Document not found. Please upload first." }
```
- User hasn't uploaded document
- Frontend: Disable question/summary buttons until upload complete

**Error: "No file provided"**
- User clicked submit without selecting file
- Frontend: Validate file selection before API call

**Error: "Unsupported file format"**
- User uploaded wrong file type
- Frontend: Use `accept=".pdf,.docx"` on file input

**Error: "No text extracted"**
- PDF might be scanned images (no OCR)
- Solution: Add OCR capability or inform user

### Recommended Error UI

```javascript
const handleError = (error) => {
  if (error.message.includes('Document not found')) {
    return 'Please upload a document first.';
  } else if (error.message.includes('file')) {
    return 'Invalid file. Please upload PDF or DOCX.';
  } else {
    return 'Something went wrong. Please try again.';
  }
};
```

---

## Performance Considerations

### Response Times

- **Upload**: 5-30 seconds (depends on document size)
  - Constitution of Kenya (~200 pages): ~15 seconds
  
- **Ask Question**: 3-8 seconds
  - Semantic search: <1 second
  - GPT response: 2-7 seconds
  
- **Summary**: 30-90 seconds
  - Depends on document length
  - Max 50 chunks analyzed (token limits)

### Optimization Tips

1. **Show Loading States**
```javascript
const [loading, setLoading] = useState({
  upload: false,
  question: false,
  summary: false
});
```

2. **Cache Summaries**
```javascript
// Store generated summary in localStorage
localStorage.setItem(`summary_${userId}`, summary);
```

3. **Progressive Loading**
```javascript
// For long summaries, stream response
// (Requires backend modification for streaming)
```

---

## Security Considerations

### Production Recommendations

1. **Add Authentication**
```javascript
// JWT token in headers
headers: {
  'Authorization': `Bearer ${userToken}`,
  'Content-Type': 'application/json'
}
```

2. **Rate Limiting**
```python
# Install: pip install flask-limiter
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/ask', methods=['POST'])
@limiter.limit("10 per minute")  # Max 10 questions per minute
def ask_question():
    # ...
```

3. **File Size Limits**
```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
```

4. **Virus Scanning**
```python
# Before processing, scan uploaded files
import clamd
cd = clamd.ClamdUnixSocket()
scan_result = cd.scan(filepath)
```

5. **HTTPS Only in Production**
```python
# Force HTTPS
if not request.is_secure:
    return redirect(request.url.replace('http://', 'https://'))
```

---

## Database Integration (Optional)

For production, consider storing document metadata in a database:

```python
# Using SQLite example
import sqlite3

def init_db():
    conn = sqlite3.connect('constitution.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS documents
                 (user_id TEXT, filename TEXT, upload_date TEXT, 
                  total_chunks INTEGER, file_path TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS qa_history
                 (user_id TEXT, question TEXT, answer TEXT, 
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_qa_history(user_id, question, answer):
    conn = sqlite3.connect('constitution.db')
    c = conn.cursor()
    c.execute('INSERT INTO qa_history VALUES (?, ?, ?, ?)',
              (user_id, question, answer, datetime.now().isoformat()))
    conn.commit()
    conn.close()
```

**Add endpoint to get history:**
```python
@app.route('/history/<user_id>', methods=['GET'])
def get_qa_history(user_id):
    conn = sqlite3.connect('constitution.db')
    c = conn.cursor()
    c.execute('SELECT question, answer, timestamp FROM qa_history 
               WHERE user_id=? ORDER BY timestamp DESC LIMIT 20', 
               (user_id,))
    history = [{'question': q, 'answer': a, 'timestamp': t} 
               for q, a, t in c.fetchall()]
    conn.close()
    return jsonify(history)
```

---

## Advanced Features to Add

### 1. Multi-Document Comparison

```python
@app.route('/compare', methods=['POST'])
def compare_documents():
    """Compare two constitutions"""
    data = request.json
    user_id1 = data.get('user_id1')
    user_id2 = data.get('user_id2')
    aspect = data.get('aspect')  # e.g., "rights and freedoms"
    
    # Get summaries from both documents about the aspect
    results1 = semantic_search(user_id1, aspect, k=5)
    results2 = semantic_search(user_id2, aspect, k=5)
    
    # Generate comparison using GPT
    comparison_prompt = PromptTemplate(
        input_variables=["doc1", "doc2", "aspect"],
        template="""Compare these two constitutional documents on: {aspect}

Document 1:
{doc1}

Document 2:
{doc2}

Provide a comparative analysis highlighting similarities, differences, and unique provisions."""
    )
    
    # Return comparison
```

### 2. Article/Section Extraction

```python
@app.route('/extract_article', methods=['POST'])
def extract_article():
    """Extract specific article or section"""
    data = request.json
    user_id = data.get('user_id')
    article_number = data.get('article_number')  # e.g., "Article 43"
    
    # Search for specific article
    results = semantic_search(user_id, f"Article {article_number}", k=3)
    
    return jsonify({
        "article_number": article_number,
        "content": results[0]['chunk_text'] if results else None
    })
```

### 3. Related Questions Suggestions

```python
@app.route('/suggest_questions', methods=['POST'])
def suggest_questions():
    """Suggest related questions based on current question"""
    data = request.json
    question = data.get('question')
    
    prompt = PromptTemplate(
        input_variables=["question"],
        template="""Based on this question about a constitution: "{question}"

Suggest 5 related follow-up questions that would help users understand the topic better.

Related questions:"""
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    suggestions = chain.run({"question": question})
    
    return jsonify({
        "original_question": question,
        "suggestions": suggestions.strip().split('\n')
    })
```

### 4. Simplified Language Mode

```python
@app.route('/ask_simple', methods=['POST'])
def ask_simple():
    """Answer in simplified language for general public"""
    # Same as /ask but with modified prompt
    qa_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""Explain this constitutional provision in simple, everyday language that a high school student can understand. Avoid legal jargon.

Context: {context}
Question: {question}

Simple explanation:"""
    )
    # Process and return
```

---

## Testing Checklist

### Functional Tests

- [ ] Upload PDF successfully
- [ ] Upload DOCX successfully
- [ ] Reject unsupported file types
- [ ] Handle corrupted files gracefully
- [ ] Ask question and get relevant answer
- [ ] Ask follow-up questions
- [ ] Generate summary
- [ ] Download summary as DOCX
- [ ] Delete document
- [ ] Handle missing user_id
- [ ] Handle non-existent user_id

### Performance Tests

- [ ] Upload 1MB document < 10 seconds
- [ ] Upload 10MB document < 30 seconds
- [ ] Question response < 10 seconds
- [ ] Summary generation < 90 seconds
- [ ] Handle 10 concurrent users
- [ ] Memory usage stays under 2GB

### Security Tests

- [ ] SQL injection attempts rejected
- [ ] File upload size limits enforced
- [ ] XSS attempts sanitized
- [ ] CORS configured correctly
- [ ] Rate limiting works
- [ ] Unauthorized access blocked

---

## Deployment Checklist

### Pre-Deployment

- [ ] Set `debug=False` in production
- [ ] Use environment variables for all secrets
- [ ] Configure proper logging
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Configure backup strategy
- [ ] Test on production-like environment
- [ ] Load testing completed
- [ ] Security audit completed

### Production Setup

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 main:app

# Or use systemd service
sudo nano /etc/systemd/system/constitution-api.service
```

**systemd service file:**
```ini
[Unit]
Description=Constitution Q&A API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/constitution-api
Environment="PATH=/var/www/constitution-api/venv/bin"
Environment="OPENAI_API_KEY=your_key_here"
ExecStart=/var/www/constitution-api/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 main:app

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120s;
        client_max_body_size 50M;
    }
}
```

---

## Troubleshooting

### Issue: "Slow summary generation"

**Solutions:**
- Reduce chunks analyzed (lower max_chunks)
- Use GPT-3.5-turbo instead of GPT-4o
- Implement streaming responses
- Cache common summaries

### Issue: "Out of memory"

**Solutions:**
- Limit concurrent users
- Clear user_documents dict periodically
- Use Redis for session storage
- Implement document expiry (auto-delete after 24h)

### Issue: "Poor answer quality"

**Solutions:**
- Increase k parameter in semantic search
- Improve chunking strategy (smaller chunks)
- Fine-tune embedding model on legal text
- Add more context in prompts

---

## Cost Estimation

### OpenAI API Costs (GPT-4o)

**Per Question:**
- Input: ~2,000 tokens (context + question)
- Output: ~500 tokens (answer)
- Cost: ~$0.025 per question

**Per Summary:**
- Input: ~10,000 tokens (large context)
- Output: ~1,500 tokens (summary)
- Cost: ~$0.15 per summary

**Monthly Estimates:**
- 1,000 questions: ~$25
- 100 summaries: ~$15
- Total: ~$40/month

### Infrastructure Costs

**Minimum Setup:**
- VPS (2GB RAM, 2 CPU): ~$10-20/month
- Domain + SSL: ~$15/year
- Total: ~$12-22/month

**Production Setup:**
- VPS (8GB RAM, 4 CPU): ~$40/month
- Load Balancer: ~$10/month
- Monitoring: ~$10/month
- Total: ~$60/month

---

## Maintenance Schedule

### Daily
- Check error logs
- Monitor API usage
- Verify system health

### Weekly
- Review user feedback
- Update document corpus if needed
- Check disk space
- Backup database

### Monthly
- Update dependencies
- Review costs
- Performance optimization
- Security patches

### Quarterly
- Major feature updates
- User survey
- Comprehensive testing
- Disaster recovery drill

---

## Support Documentation

### For End Users

**FAQ Document:**

**Q: What file formats are supported?**
A: PDF and DOCX files up to 50MB.

**Q: How accurate are the answers?**
A: Answers are based on the exact text in your uploaded document. Always verify critical information.

**Q: Can I upload multiple documents?**
A: Currently one document per user. Delete your current document to upload a new one.

**Q: How long is my document stored?**
A: Documents are stored for your session. Consider them temporary.

**Q: Is my data private?**
A: Documents are processed through OpenAI's API. See their privacy policy for details.

### For Developers

**API Documentation:**
- Swagger/OpenAPI spec
- Rate limits
- Authentication methods
- Error codes
- Example requests

**Integration Guide:**
- SDK examples
- Webhook setup
- Batch processing
- Custom deployments

---

## Conclusion

This Constitution Q&A system provides:
- ✅ Easy document upload
- ✅ Natural language questions
- ✅ AI-powered answers with sources
- ✅ Comprehensive summaries
- ✅ Downloadable reports
- ✅ Production-ready architecture

**Next Steps:**
1. Test thoroughly with Postman
2. Integrate with your frontend
3. Add authentication
4. Deploy to production
5. Gather user feedback
6. Iterate and improve