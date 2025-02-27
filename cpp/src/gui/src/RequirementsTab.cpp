#include "RequirementsTab.hpp"
#include "RequirementsManager.hpp"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QToolBar>
#include <QTableView>
#include <QTreeView>
#include <QPushButton>
#include <QComboBox>
#include <QLabel>
#include <QMenu>
#include <QMessageBox>
#include <QFileDialog>
#include <QSplitter>

struct RequirementsTab::Private {
    std::unique_ptr<RequirementsManager> manager;
    
    // UI Components
    QTableView* requirementsTable{nullptr};
    QTreeView* traceabilityTree{nullptr};
    QTableView* vvMatrix{nullptr};
    QWidget* systemVView{nullptr};
    
    // Toolbars
    QToolBar* mainToolbar{nullptr};
    QToolBar* filterToolbar{nullptr};
    
    // Filters
    QComboBox* typeFilter{nullptr};
    QComboBox* statusFilter{nullptr};
    QComboBox* priorityFilter{nullptr};
    
    // Models
    QStandardItemModel* requirementsModel{nullptr};
    QStandardItemModel* traceabilityModel{nullptr};
    QStandardItemModel* vvModel{nullptr};
    QStandardItemModel* systemVModel{nullptr};
};

RequirementsTab::RequirementsTab(QWidget* parent)
    : QWidget(parent)
    , d(std::make_unique<Private>())
{
    d->manager = std::make_unique<RequirementsManager>();
    setupUi();
    loadRequirements();
}

RequirementsTab::~RequirementsTab() = default;

void RequirementsTab::setupUi()
{
    auto* mainLayout = new QVBoxLayout(this);
    
    // Setup toolbars
    setupToolbar();
    mainLayout->addWidget(d->mainToolbar);
    
    // Setup filters
    auto* filterWidget = new QWidget(this);
    auto* filterLayout = new QHBoxLayout(filterWidget);
    
    d->typeFilter = new QComboBox(filterWidget);
    d->typeFilter->addItems({"All Types", "Functional", "Performance", "Interface", 
                            "Security", "Safety", "Environmental", "Regulatory", "UserInterface"});
    
    d->statusFilter = new QComboBox(filterWidget);
    d->statusFilter->addItems({"All Status", "Draft", "Review", "Approved", "Implemented",
                              "Verified", "Validated", "Rejected", "Obsolete"});
    
    d->priorityFilter = new QComboBox(filterWidget);
    d->priorityFilter->addItems({"All Priorities", "Critical", "High", "Medium", "Low"});
    
    filterLayout->addWidget(new QLabel(tr("Type:")));
    filterLayout->addWidget(d->typeFilter);
    filterLayout->addWidget(new QLabel(tr("Status:")));
    filterLayout->addWidget(d->statusFilter);
    filterLayout->addWidget(new QLabel(tr("Priority:")));
    filterLayout->addWidget(d->priorityFilter);
    filterLayout->addStretch();
    
    mainLayout->addWidget(filterWidget);
    
    // Main content area with splitter
    auto* splitter = new QSplitter(Qt::Horizontal, this);
    mainLayout->addWidget(splitter);
    
    // Left side - Requirements table
    d->requirementsTable = new QTableView(splitter);
    d->requirementsTable->setSelectionBehavior(QAbstractItemView::SelectRows);
    d->requirementsTable->setSelectionMode(QAbstractItemView::SingleSelection);
    d->requirementsTable->setContextMenuPolicy(Qt::CustomContextMenu);
    
    // Right side - Tabbed widget for different views
    auto* rightTabs = new QTabWidget(splitter);
    
    // Traceability View
    d->traceabilityTree = new QTreeView(rightTabs);
    rightTabs->addTab(d->traceabilityTree, tr("Traceability"));
    
    // V&V Matrix
    d->vvMatrix = new QTableView(rightTabs);
    rightTabs->addTab(d->vvMatrix, tr("V&V Matrix"));
    
    // System V View
    d->systemVView = new QWidget(rightTabs);
    rightTabs->addTab(d->systemVView, tr("System V"));
    
    // Set up models
    setupRequirementsTable();
    setupTraceabilityView();
    setupSystemVView();
    
    // Connect signals
    connect(d->typeFilter, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &RequirementsTab::updateFilters);
    connect(d->statusFilter, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &RequirementsTab::updateFilters);
    connect(d->priorityFilter, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &RequirementsTab::updateFilters);
    
    connect(d->requirementsTable, &QTableView::customContextMenuRequested,
            this, &RequirementsTab::setupContextMenu);
}

void RequirementsTab::setupToolbar()
{
    d->mainToolbar = new QToolBar(this);
    
    // Requirements actions
    d->mainToolbar->addAction(tr("Add Requirement"), this, &RequirementsTab::addRequirement);
    d->mainToolbar->addAction(tr("Edit Requirement"), this, &RequirementsTab::editRequirement);
    d->mainToolbar->addAction(tr("Delete Requirement"), this, &RequirementsTab::deleteRequirement);
    d->mainToolbar->addSeparator();
    
    // Import/Export actions
    d->mainToolbar->addAction(tr("Import"), [this]() {
        QString filePath = QFileDialog::getOpenFileName(this, tr("Import Requirements"),
            QString(), tr("Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*.*)"));
        if (!filePath.isEmpty()) {
            importRequirements(filePath);
        }
    });
    
    d->mainToolbar->addAction(tr("Export"), [this]() {
        QString filePath = QFileDialog::getSaveFileName(this, tr("Export Requirements"),
            QString(), tr("Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*.*)"));
        if (!filePath.isEmpty()) {
            exportRequirements(filePath);
        }
    });
    
    d->mainToolbar->addSeparator();
    
    // Report actions
    auto* reportsMenu = new QMenu(tr("Reports"), this);
    reportsMenu->addAction(tr("Traceability Matrix"), this, &RequirementsTab::showTraceabilityMatrix);
    reportsMenu->addAction(tr("V&V Matrix"), this, &RequirementsTab::showVVMatrix);
    reportsMenu->addAction(tr("System V Diagram"), this, &RequirementsTab::showSystemVDiagram);
    
    auto* reportsButton = new QToolButton(this);
    reportsButton->setMenu(reportsMenu);
    reportsButton->setPopupMode(QToolButton::InstantPopup);
    reportsButton->setText(tr("Reports"));
    reportsButton->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    
    d->mainToolbar->addWidget(reportsButton);
}

void RequirementsTab::setupContextMenu()
{
    auto index = d->requirementsTable->currentIndex();
    if (!index.isValid()) return;
    
    auto reqId = d->requirementsModel->data(
        d->requirementsModel->index(index.row(), 0)).toString();
    
    QMenu menu(this);
    menu.addAction(tr("Edit"), [this, reqId]() {
        editRequirement();
    });
    
    menu.addAction(tr("Delete"), [this, reqId]() {
        deleteRequirement();
    });
    
    menu.addSeparator();
    
    // Link submenus
    auto* linkMenu = menu.addMenu(tr("Link to..."));
    linkMenu->addAction(tr("Component"), [this, reqId]() {
        // Show component selection dialog
    });
    linkMenu->addAction(tr("Test Case"), [this, reqId]() {
        // Show test case selection dialog
    });
    linkMenu->addAction(tr("Use Case"), [this, reqId]() {
        // Show use case selection dialog
    });
    linkMenu->addAction(tr("System V Document"), [this, reqId]() {
        // Show document selection dialog
    });
    
    // Status submenus
    auto* verificationMenu = menu.addMenu(tr("Verification Status"));
    verificationMenu->addAction(tr("Not Started"));
    verificationMenu->addAction(tr("In Progress"));
    verificationMenu->addAction(tr("Passed"));
    verificationMenu->addAction(tr("Failed"));
    verificationMenu->addAction(tr("Blocked"));
    
    auto* validationMenu = menu.addMenu(tr("Validation Status"));
    validationMenu->addAction(tr("Not Started"));
    validationMenu->addAction(tr("In Progress"));
    validationMenu->addAction(tr("Passed"));
    validationMenu->addAction(tr("Failed"));
    validationMenu->addAction(tr("Blocked"));
    
    menu.exec(QCursor::pos());
}

void RequirementsTab::loadRequirements()
{
    auto requirements = d->manager->getAllRequirements();
    
    d->requirementsModel->clear();
    d->requirementsModel->setHorizontalHeaderLabels({
        tr("ID"), tr("Title"), tr("Type"), tr("Priority"), tr("Status"),
        tr("Created Date"), tr("Modified Date")
    });
    
    for (const auto& req : requirements) {
        QList<QStandardItem*> row;
        row << new QStandardItem(req.id)
            << new QStandardItem(req.title)
            << new QStandardItem(toString(req.type))
            << new QStandardItem(toString(req.priority))
            << new QStandardItem(toString(req.status))
            << new QStandardItem(req.createdDate.toString())
            << new QStandardItem(req.modifiedDate.toString());
        
        d->requirementsModel->appendRow(row);
    }
    
    updateFilters();
}
