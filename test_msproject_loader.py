"""Quick test for MS Project loader"""
import io
from src.eva_rag.loaders.mpp_loader import MSProjectLoader

# Sample MS Project XML (simplified)
project_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Project xmlns="http://schemas.microsoft.com/project">
    <Title>Employment Data Collection Project</Title>
    <Author>Statistics Canada</Author>
    <Company>Government of Canada</Company>
    <StartDate>2024-01-01T00:00:00</StartDate>
    <FinishDate>2024-12-31T00:00:00</FinishDate>
    <CreationDate>2024-01-01T00:00:00</CreationDate>
    
    <Tasks>
        <Task>
            <UID>1</UID>
            <ID>1</ID>
            <Name>Employment Survey Phase 1</Name>
            <Start>2024-01-01T00:00:00</Start>
            <Finish>2024-03-31T00:00:00</Finish>
            <Duration>PT720H0M0S</Duration>
            <PercentComplete>100</PercentComplete>
            <OutlineLevel>1</OutlineLevel>
            <Summary>1</Summary>
        </Task>
        <Task>
            <UID>2</UID>
            <ID>2</ID>
            <Name>Data Collection - Ontario</Name>
            <Start>2024-01-15T00:00:00</Start>
            <Finish>2024-02-28T00:00:00</Finish>
            <Duration>PT350H0M0S</Duration>
            <PercentComplete>100</PercentComplete>
            <OutlineLevel>2</OutlineLevel>
            <Critical>1</Critical>
        </Task>
        <Task>
            <UID>3</UID>
            <ID>3</ID>
            <Name>Data Collection - Quebec</Name>
            <Start>2024-01-15T00:00:00</Start>
            <Finish>2024-02-28T00:00:00</Finish>
            <Duration>PT350H0M0S</Duration>
            <PercentComplete>100</PercentComplete>
            <OutlineLevel>2</OutlineLevel>
        </Task>
        <Task>
            <UID>4</UID>
            <ID>4</ID>
            <Name>Data Analysis Complete</Name>
            <Start>2024-03-31T00:00:00</Start>
            <Finish>2024-03-31T00:00:00</Finish>
            <Duration>PT0H0M0S</Duration>
            <PercentComplete>100</PercentComplete>
            <OutlineLevel>1</OutlineLevel>
            <Milestone>1</Milestone>
        </Task>
    </Tasks>
    
    <Resources>
        <Resource>
            <UID>1</UID>
            <ID>1</ID>
            <Name>Research Team</Name>
            <Type>1</Type>
            <EmailAddress>research@statcan.gc.ca</EmailAddress>
            <StandardRate>75</StandardRate>
            <Work>PT1200H0M0S</Work>
        </Resource>
        <Resource>
            <UID>2</UID>
            <ID>2</ID>
            <Name>Data Analysts</Name>
            <Type>1</Type>
            <EmailAddress>analysts@statcan.gc.ca</EmailAddress>
            <StandardRate>85</StandardRate>
            <Work>PT800H0M0S</Work>
        </Resource>
    </Resources>
    
    <Assignments>
        <Assignment>
            <UID>1</UID>
            <TaskUID>2</TaskUID>
            <ResourceUID>1</ResourceUID>
            <Units>1.0</Units>
            <Work>PT350H0M0S</Work>
        </Assignment>
        <Assignment>
            <UID>2</UID>
            <TaskUID>3</TaskUID>
            <ResourceUID>1</ResourceUID>
            <Units>1.0</Units>
            <Work>PT350H0M0S</Work>
        </Assignment>
    </Assignments>
</Project>
"""

def test_msproject():
    print('Testing MS Project Loader...')
    
    xml_stream = io.BytesIO(project_xml.encode('utf-8'))
    loader = MSProjectLoader(
        include_resources=True,
        include_assignments=True
    )
    
    doc = loader.load_from_stream(xml_stream)
    
    print(f'✅ MS Project loaded successfully')
    print(f'   Project: {doc.metadata["project_name"]}')
    print(f'   Tasks: {doc.metadata["task_count"]}')
    print(f'   Resources: {doc.metadata["resource_count"]}')
    print(f'   Assignments: {doc.metadata["assignment_count"]}')
    print(f'   Start: {doc.metadata["project_start"]}')
    print(f'   Finish: {doc.metadata["project_finish"]}')
    
    print('\n=== Generated Markdown Preview ===')
    print(doc.text[:800])
    print('\n...(truncated)')
    
    return doc

if __name__ == '__main__':
    print('=== Testing MS Project Loader ===\n')
    doc = test_msproject()
    print('\n✅ MS Project loader working correctly!')
