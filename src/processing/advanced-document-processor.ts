/**
 * Advanced Document Processor Implementation
 * Adapts Microsoft Info Assistant patterns for EVA's TypeScript architecture
 */

import { 
  IAdvancedDocumentProcessor,
  ParsedDocument, 
  DocumentChunk, 
  DocumentMetadata,
  ContentType,
  ProcessingStatus,
  DocumentTable,
  DocumentImage,
  DocumentProcessorConfig 
} from './types';
import { DocumentAnalysisClient, AzureKeyCredential } from '@azure/ai-form-recognizer';
import { BlobServiceClient } from '@azure/storage-blob';
import { CosmosClient } from '@azure/cosmos';
import { DefaultAzureCredential } from '@azure/identity';

/**
 * Advanced Document Processor
 * Implements Info Assistant's multi-format parsing with EVA's architecture
 */
export class AdvancedDocumentProcessor implements IAdvancedDocumentProcessor {
  private documentIntelligenceClient: DocumentAnalysisClient;
  private blobServiceClient: BlobServiceClient;
  private cosmosClient: CosmosClient;
  private config: DocumentProcessorConfig;

  constructor(config: DocumentProcessorConfig) {
    this.config = config;
    
    // Initialize Azure Document Intelligence (Form Recognizer)
    const credential = new DefaultAzureCredential();
    this.documentIntelligenceClient = new DocumentAnalysisClient(
      config.azureFormRecognizerEndpoint,
      credential
    );
    
    // Initialize Blob Storage for document storage
    this.blobServiceClient = new BlobServiceClient(
      `https://${config.blobStorageAccount}.blob.core.windows.net`,
      credential
    );
    
    // Initialize Cosmos DB for status tracking
    this.cosmosClient = new CosmosClient({
      endpoint: config.cosmosDbEndpoint,
      aadCredentials: credential
    });
  }

  /**
   * Parse document using Azure Document Intelligence
   * Supports 20+ file formats with advanced layout analysis
   */
  async parseDocument(file: File | Buffer, fileName: string): Promise<ParsedDocument> {
    const documentId = this.generateDocumentId(fileName);
    
    try {
      // Log processing start
      await this.updateProcessingStatus(documentId, ProcessingStatus.PROCESSING, {
        fileName,
        stage: 'document_analysis',
        timestamp: new Date().toISOString()
      });

      // Detect document format
      const fileBuffer = file instanceof File ? await file.arrayBuffer() : file;
      const format = this.detectFormatFromFileName(fileName);
      
      // Use appropriate analysis model based on format
      const modelId = this.getAnalysisModel(format);
      
      // Analyze document with Azure Document Intelligence
      const poller = await this.documentIntelligenceClient.beginAnalyzeDocument(
        modelId,
        new Uint8Array(fileBuffer),
        {
          pages: '1-', // Analyze all pages
          locale: 'en-US'
        }
      );
      
      const result = await poller.pollUntilDone();
      
      // Build document map (adapted from Info Assistant pattern)
      const documentMetadata = this.buildDocumentMetadata(fileName, result, format);
      
      // Extract content with structure preservation
      const content = this.extractContentWithStructure(result);
      
      // Perform intelligent chunking
      const chunks = await this.chunkBySection(content, documentMetadata);
      
      // Process tables and images
      const tables = await this.processTables({ 
        id: documentId, 
        metadata: documentMetadata, 
        content,
        chunks: [],
        tables: [],
        images: [],
        processingStatus: ProcessingStatus.PROCESSING 
      });
      
      const images = await this.processImages({
        id: documentId,
        metadata: documentMetadata,
        content,
        chunks: [],
        tables: [],
        images: [],
        processingStatus: ProcessingStatus.PROCESSING
      });

      const parsedDocument: ParsedDocument = {
        id: documentId,
        metadata: documentMetadata,
        content,
        chunks,
        tables,
        images,
        processingStatus: ProcessingStatus.COMPLETED
      };

      // Log successful completion
      await this.updateProcessingStatus(documentId, ProcessingStatus.COMPLETED, {
        chunksCount: chunks.length,
        tablesCount: tables.length,
        imagesCount: images.length,
        contentLength: content.length
      });

      return parsedDocument;
      
    } catch (error) {
      await this.updateProcessingStatus(documentId, ProcessingStatus.FAILED, {
        error: error.message,
        stage: 'document_analysis'
      });
      throw error;
    }
  }

  /**
   * Intelligent chunking by section (Info Assistant pattern)
   * Target: 750 tokens per chunk with section-based boundaries
   */
  async chunkBySection(
    content: string,
    metadata: DocumentMetadata,
    maxTokens: number = 750
  ): Promise<DocumentChunk[]> {
    const chunks: DocumentChunk[] = [];
    
    // Use section-based chunking similar to Info Assistant
    let currentChunk = '';
    let currentSection = '';
    let currentSubsection = '';
    let chunkIndex = 0;
    
    for (let i = 0; i < metadata.structure.length; i++) {
      const structureItem = metadata.structure[i];
      
      // Update section context
      if (structureItem.type === 'section') {
        currentSection = structureItem.content;
        currentSubsection = '';
      } else if (structureItem.type === 'subsection') {
        currentSubsection = structureItem.content;
      }
      
      // Estimate token count (rough approximation: 1 token ≈ 4 characters)
      const potentialChunk = currentChunk + '\n' + structureItem.content;
      const estimatedTokens = Math.ceil(potentialChunk.length / 4);
      
      if (estimatedTokens > maxTokens && currentChunk.length > 0) {
        // Create chunk with current content
        chunks.push({
          id: `${metadata.fileName}_chunk_${chunkIndex}`,
          content: currentChunk.trim(),
          metadata: {
            documentId: metadata.fileName,
            fileName: metadata.fileName,
            section: currentSection,
            subsection: currentSubsection,
            chunkIndex,
            tokenCount: Math.ceil(currentChunk.length / 4),
            contentType: this.getPrimaryContentType(currentChunk, metadata)
          },
          citations: [metadata.fileUri]
        });
        
        chunkIndex++;
        currentChunk = structureItem.content;
      } else {
        currentChunk += (currentChunk.length > 0 ? '\n' : '') + structureItem.content;
      }
    }
    
    // Add final chunk if there's remaining content
    if (currentChunk.trim().length > 0) {
      chunks.push({
        id: `${metadata.fileName}_chunk_${chunkIndex}`,
        content: currentChunk.trim(),
        metadata: {
          documentId: metadata.fileName,
          fileName: metadata.fileName,
          section: currentSection,
          subsection: currentSubsection,
          chunkIndex,
          tokenCount: Math.ceil(currentChunk.length / 4),
          contentType: this.getPrimaryContentType(currentChunk, metadata)
        },
        citations: [metadata.fileUri]
      });
    }
    
    return chunks;
  }

  /**
   * Enrich chunks with enhanced metadata (Info Assistant pattern)
   */
  async enrichWithMetadata(
    chunks: DocumentChunk[],
    document: ParsedDocument
  ): Promise<DocumentChunk[]> {
    return chunks.map(chunk => ({
      ...chunk,
      metadata: {
        ...chunk.metadata,
        // Add document title for context
        documentTitle: this.extractDocumentTitle(document),
        // Add enhanced section hierarchy
        sectionHierarchy: this.buildSectionHierarchy(chunk, document),
        // Add content classification
        contentClassification: this.classifyContent(chunk.content),
        // Add processing timestamp
        processingTimestamp: new Date().toISOString()
      }
    }));
  }

  /**
   * Process tables with structure preservation
   */
  async processTables(document: ParsedDocument): Promise<DocumentTable[]> {
    // Implementation would process tables from Document Intelligence results
    // This is a simplified version - full implementation would parse table structure
    return [];
  }

  /**
   * Process images with OCR and description
   */
  async processImages(document: ParsedDocument): Promise<DocumentImage[]> {
    // Implementation would process images from Document Intelligence results
    // This is a simplified version - full implementation would extract image data
    return [];
  }

  /**
   * Update processing status in Cosmos DB
   */
  async updateProcessingStatus(
    documentId: string,
    status: ProcessingStatus,
    details?: Record<string, any>
  ): Promise<void> {
    const database = this.cosmosClient.database(this.config.statusDatabase);
    const container = database.container(this.config.statusContainer);
    
    const statusItem = {
      id: documentId,
      documentId,
      status,
      timestamp: new Date().toISOString(),
      details: details || {},
      // Use hierarchical partition key for tenant isolation
      partitionKey: [documentId.split('_')[0], documentId] // [tenantId, documentId]
    };
    
    await container.items.upsert(statusItem);
  }

  // Private helper methods
  private generateDocumentId(fileName: string): string {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const sanitized = fileName.replace(/[^a-zA-Z0-9.-]/g, '_');
    return `doc_${timestamp}_${sanitized}`;
  }

  private detectFormatFromFileName(fileName: string): string {
    const extension = fileName.split('.').pop()?.toLowerCase();
    return extension || 'unknown';
  }

  private getAnalysisModel(format: string): string {
    // Map file formats to appropriate Document Intelligence models
    switch (format) {
      case 'pdf':
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'tiff':
        return 'prebuilt-layout';
      case 'docx':
      case 'pptx':
      case 'xlsx':
        return 'prebuilt-document';
      default:
        return 'prebuilt-read';
    }
  }

  private buildDocumentMetadata(fileName: string, analysisResult: any, format: string): DocumentMetadata {
    // Adapt Info Assistant's document map building logic
    return {
      fileName,
      fileUri: `processed/${fileName}`,
      fileType: format,
      contentType: [],
      tableIndex: [],
      structure: [],
      processingTimestamp: new Date()
    };
  }

  private extractContentWithStructure(analysisResult: any): string {
    // Extract content while preserving document structure
    return analysisResult.content || '';
  }

  private getPrimaryContentType(content: string, metadata: DocumentMetadata): ContentType {
    // Analyze content to determine primary type
    if (content.includes('|') && content.includes('\n')) {
      return ContentType.TABLE_CHAR;
    }
    if (content.length < 100) {
      return ContentType.TITLE;
    }
    return ContentType.REGULAR_CONTENT;
  }

  private extractDocumentTitle(document: ParsedDocument): string {
    // Extract document title from structure
    const titleStructure = document.metadata.structure.find(s => s.type === 'title');
    return titleStructure?.content || document.metadata.fileName;
  }

  private buildSectionHierarchy(chunk: DocumentChunk, document: ParsedDocument): string[] {
    // Build section hierarchy for enhanced context
    const hierarchy: string[] = [];
    if (chunk.metadata.section) hierarchy.push(chunk.metadata.section);
    if (chunk.metadata.subsection) hierarchy.push(chunk.metadata.subsection);
    return hierarchy;
  }

  private classifyContent(content: string): string {
    // Classify content type for better retrieval
    if (content.includes('table') || content.includes('|')) return 'tabular';
    if (content.includes('figure') || content.includes('image')) return 'visual';
    if (content.includes('code') || content.includes('```')) return 'code';
    return 'text';
  }
}
