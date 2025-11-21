/**
 * Advanced Document Processing Pipeline
 * Inspired by Microsoft Info Assistant patterns, adapted for EVA's microservices architecture
 */

export interface DocumentMetadata {
  fileName: string;
  fileUri: string;
  fileType: string;
  contentType: ContentType[];
  tableIndex: number[];
  structure: DocumentStructure[];
  pageCount?: number;
  language?: string;
  processingTimestamp: Date;
}

export enum ContentType {
  NOT_PROCESSED = 'not_processed',
  TITLE = 'title',
  SECTION_HEADING = 'section_heading',
  REGULAR_CONTENT = 'regular_content',
  TABLE_START = 'table_start',
  TABLE_CHAR = 'table_char',
  TABLE_END = 'table_end',
  IMAGE = 'image',
  CODE_BLOCK = 'code_block'
}

export interface DocumentStructure {
  type: 'title' | 'section' | 'subsection' | 'paragraph' | 'table' | 'image';
  content: string;
  level: number;
  startOffset: number;
  endOffset: number;
  pageNumber?: number;
  confidence?: number;
}

export interface DocumentChunk {
  id: string;
  content: string;
  metadata: {
    documentId: string;
    fileName: string;
    section?: string;
    subsection?: string;
    pageNumber?: number;
    chunkIndex: number;
    tokenCount: number;
    contentType: ContentType;
  };
  embedding?: number[];
  citations: string[];
}

export interface ParsedDocument {
  id: string;
  metadata: DocumentMetadata;
  content: string;
  chunks: DocumentChunk[];
  tables: DocumentTable[];
  images: DocumentImage[];
  processingStatus: ProcessingStatus;
}

export interface DocumentTable {
  index: number;
  content: string;
  htmlContent: string;
  rowCount: number;
  columnCount: number;
  pageNumber?: number;
  boundingBox?: BoundingBox;
}

export interface DocumentImage {
  index: number;
  description?: string;
  boundingBox?: BoundingBox;
  pageNumber?: number;
  confidence?: number;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export enum ProcessingStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  RETRY = 'retry'
}

/**
 * Advanced Document Processor
 * Supports 20+ file formats with intelligent chunking and metadata enrichment
 */
export interface IAdvancedDocumentProcessor {
  /**
   * Parse document using Azure Document Intelligence
   * Supports: PDF, DOCX, PPTX, XLSX, HTML, TXT, MD, CSV, JSON, XML, RTF, ODT, ODS, ODP
   */
  parseDocument(file: File | Buffer, fileName: string): Promise<ParsedDocument>;
  
  /**
   * Intelligent chunking by section with metadata preservation
   * Target: 750 tokens per chunk with no overlap (Info Assistant pattern)
   */
  chunkBySection(
    content: string, 
    metadata: DocumentMetadata,
    maxTokens?: number
  ): Promise<DocumentChunk[]>;
  
  /**
   * Enrich chunks with contextual metadata
   * Includes document title, section, subsection for enhanced retrieval
   */
  enrichWithMetadata(
    chunks: DocumentChunk[],
    document: ParsedDocument
  ): Promise<DocumentChunk[]>;
  
  /**
   * Extract and process tables with structure preservation
   */
  processTables(document: ParsedDocument): Promise<DocumentTable[]>;
  
  /**
   * Extract and analyze images with OCR and description
   */
  processImages(document: ParsedDocument): Promise<DocumentImage[]>;
  
  /**
   * Track processing status with detailed logging
   */
  updateProcessingStatus(
    documentId: string, 
    status: ProcessingStatus,
    details?: Record<string, any>
  ): Promise<void>;
}

/**
 * Configuration for document processing
 */
export interface DocumentProcessorConfig {
  // Chunking configuration
  maxTokensPerChunk: number;
  chunkOverlap: number;
  preserveStructure: boolean;
  
  // Azure Document Intelligence settings
  azureFormRecognizerEndpoint: string;
  azureFormRecognizerApiVersion: string;
  
  // Storage configuration
  blobStorageAccount: string;
  contentContainer: string;
  logContainer: string;
  
  // Processing options
  enableOcr: boolean;
  enableTableExtraction: boolean;
  enableImageAnalysis: boolean;
  supportedFormats: string[];
  
  // Cosmos DB configuration for status tracking
  cosmosDbEndpoint: string;
  statusDatabase: string;
  statusContainer: string;
}

/**
 * Status logging interface for processing pipeline
 */
export interface IStatusLogger {
  logProcessingStart(documentId: string, fileName: string): Promise<void>;
  logProcessingProgress(
    documentId: string, 
    stage: string, 
    progress: number,
    details?: Record<string, any>
  ): Promise<void>;
  logProcessingComplete(
    documentId: string, 
    result: ParsedDocument
  ): Promise<void>;
  logProcessingError(
    documentId: string, 
    error: Error, 
    stage: string
  ): Promise<void>;
  
  getProcessingStatus(documentId: string): Promise<ProcessingStatus>;
  getProcessingLogs(documentId: string): Promise<any[]>;
}

/**
 * Multi-format document parser interface
 */
export interface IMultiFormatParser {
  // PDF processing with advanced layout analysis
  parsePdf(file: Buffer): Promise<ParsedDocument>;
  
  // Office document processing (DOCX, PPTX, XLSX)
  parseOfficeDocument(file: Buffer, format: string): Promise<ParsedDocument>;
  
  // Web content processing (HTML, XML)
  parseWebContent(content: string, format: string): Promise<ParsedDocument>;
  
  // Structured data processing (JSON, CSV)
  parseStructuredData(content: string, format: string): Promise<ParsedDocument>;
  
  // Plain text processing (TXT, MD, RTF)
  parseTextDocument(content: string, format: string): Promise<ParsedDocument>;
  
  // Detect file format from content or extension
  detectFormat(file: Buffer, fileName: string): Promise<string>;
}
