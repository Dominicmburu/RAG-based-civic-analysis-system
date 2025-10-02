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
  'Content-Type': 'application# RAG-based-civic-analysis-system
