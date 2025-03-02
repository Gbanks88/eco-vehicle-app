// Builder API paths for Swagger documentation
export const builderPaths = {
  '/api/builder/components': {
    get: {
      summary: 'List available components',
      tags: ['Builder'],
      responses: {
        '200': {
          description: 'List of available components',
          content: {
            'application/json': {
              schema: {
                type: 'object',
                properties: {
                  components: {
                    type: 'object',
                    additionalProperties: {
                      $ref: '#/components/schemas/Component'
                    }
                  },
                  categories: {
                    type: 'object',
                    additionalProperties: {
                      type: 'array',
                      items: {
                        type: 'string'
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  '/api/builder/workflows': {
    get: {
      summary: 'List workflows',
      tags: ['Builder'],
      responses: {
        '200': {
          description: 'List of workflows',
          content: {
            'application/json': {
              schema: {
                type: 'array',
                items: {
                  $ref: '#/components/schemas/Workflow'
                }
              }
            }
          }
        }
      }
    },
    post: {
      summary: 'Create workflow',
      tags: ['Builder'],
      requestBody: {
        required: true,
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/WorkflowCreate'
            }
          }
        }
      },
      responses: {
        '201': {
          description: 'Workflow created',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Workflow'
              }
            }
          }
        }
      }
    }
  },
  '/api/builder/workflows/{workflowId}': {
    get: {
      summary: 'Get workflow',
      tags: ['Builder'],
      parameters: [
        {
          name: 'workflowId',
          in: 'path',
          required: true,
          schema: {
            type: 'string'
          }
        }
      ],
      responses: {
        '200': {
          description: 'Workflow details',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Workflow'
              }
            }
          }
        }
      }
    },
    put: {
      summary: 'Update workflow',
      tags: ['Builder'],
      parameters: [
        {
          name: 'workflowId',
          in: 'path',
          required: true,
          schema: {
            type: 'string'
          }
        }
      ],
      requestBody: {
        required: true,
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/WorkflowUpdate'
            }
          }
        }
      },
      responses: {
        '200': {
          description: 'Workflow updated',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Workflow'
              }
            }
          }
        }
      }
    },
    delete: {
      summary: 'Delete workflow',
      tags: ['Builder'],
      parameters: [
        {
          name: 'workflowId',
          in: 'path',
          required: true,
          schema: {
            type: 'string'
          }
        }
      ],
      responses: {
        '204': {
          description: 'Workflow deleted'
        }
      }
    }
  },
  '/api/builder/workflows/{workflowId}/execute': {
    post: {
      summary: 'Execute workflow',
      tags: ['Builder'],
      parameters: [
        {
          name: 'workflowId',
          in: 'path',
          required: true,
          schema: {
            type: 'string'
          }
        }
      ],
      requestBody: {
        required: false,
        content: {
          'application/json': {
            schema: {
              type: 'object',
              properties: {
                context: {
                  type: 'object',
                  description: 'Workflow execution context'
                }
              }
            }
          }
        }
      },
      responses: {
        '200': {
          description: 'Workflow execution result',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/WorkflowExecution'
              }
            }
          }
        }
      }
    }
  }
};

// Builder API schemas for Swagger documentation
export const builderSchemas = {
  Component: {
    type: 'object',
    properties: {
      type: {
        type: 'string',
        enum: ['input', 'display', 'container', 'layout', 'integration', 'monitoring']
      },
      render: {
        type: 'object',
        description: 'Component rendering configuration'
      },
      validate: {
        type: 'object',
        description: 'Component validation rules'
      },
      metrics: {
        type: 'object',
        properties: {
          usage: {
            type: 'integer',
            description: 'Number of times the component has been used'
          },
          errors: {
            type: 'integer',
            description: 'Number of errors encountered'
          },
          latency: {
            type: 'array',
            items: {
              type: 'number'
            },
            description: 'Recent latency measurements in milliseconds'
          }
        }
      }
    }
  },
  Workflow: {
    type: 'object',
    properties: {
      id: {
        type: 'string'
      },
      name: {
        type: 'string'
      },
      description: {
        type: 'string'
      },
      steps: {
        type: 'array',
        items: {
          $ref: '#/components/schemas/WorkflowStep'
        }
      },
      metrics: {
        type: 'object',
        properties: {
          executions: {
            type: 'integer'
          },
          failures: {
            type: 'integer'
          },
          avgDuration: {
            type: 'number'
          }
        }
      },
      createdAt: {
        type: 'string',
        format: 'date-time'
      },
      updatedAt: {
        type: 'string',
        format: 'date-time'
      }
    }
  },
  WorkflowStep: {
    type: 'object',
    properties: {
      id: {
        type: 'string'
      },
      name: {
        type: 'string'
      },
      component: {
        type: 'string'
      },
      config: {
        type: 'object'
      },
      next: {
        type: 'array',
        items: {
          type: 'string'
        }
      }
    }
  },
  WorkflowCreate: {
    type: 'object',
    required: ['name', 'steps'],
    properties: {
      name: {
        type: 'string'
      },
      description: {
        type: 'string'
      },
      steps: {
        type: 'array',
        items: {
          $ref: '#/components/schemas/WorkflowStep'
        }
      }
    }
  },
  WorkflowUpdate: {
    type: 'object',
    properties: {
      name: {
        type: 'string'
      },
      description: {
        type: 'string'
      },
      steps: {
        type: 'array',
        items: {
          $ref: '#/components/schemas/WorkflowStep'
        }
      }
    }
  },
  WorkflowExecution: {
    type: 'object',
    properties: {
      id: {
        type: 'string'
      },
      workflowId: {
        type: 'string'
      },
      status: {
        type: 'string',
        enum: ['running', 'completed', 'failed']
      },
      startTime: {
        type: 'string',
        format: 'date-time'
      },
      endTime: {
        type: 'string',
        format: 'date-time'
      },
      duration: {
        type: 'number'
      },
      result: {
        type: 'object'
      },
      error: {
        type: 'string'
      }
    }
  }
};
